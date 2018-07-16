import math
import re
import telnetlib

from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


class TelnetConnection:
    tn = object
    bot = object
    show_log_init = bool

    full_banner = str

    def __init__(self, bot, ip, port, password, show_log_init=False):
        try:
            connection = telnetlib.Telnet(ip, port, timeout=2)
        except Exception as e:
            log_message = 'trying to establish telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        self.bot = bot
        self.show_log_init = show_log_init
        self.full_banner = ""
        self.tn = self.authenticate(connection, password)

    def authenticate(self, connection, password):
        try:
            # Waiting for the prompt.
            found_prompt = False
            while found_prompt is not True:
                telnet_response = connection.read_until(b"\r\n")
                if re.match(r"Please enter password:\r\n", telnet_response):
                    found_prompt = True

            # Sending password.
            full_auth_response = ''
            authenticated = False
            connection.write(password.encode('ascii') + b"\r\n")
            while authenticated is not True:  # loop until authenticated, it's required
                telnet_response = connection.read_until(b"\r\n")
                full_auth_response += telnet_response.rstrip()
                # last 'welcome' line from the games telnet. it might change with a new game-version
                if re.match(r"Password incorrect, please enter password:\r\n", telnet_response) is not None:
                    log_message = 'incorrect telnet password'
                    logger.critical(log_message)
                    raise ValueError
                if re.match(r"Logon successful.\r\n", telnet_response) is not None:
                    authenticated = True
            if self.show_log_init is True and full_auth_response != '':
                logger.info(full_auth_response)

            # Waiting for banner.
            full_banner = ''
            displayed_welcome = False
            while displayed_welcome is not True:  # loop until ready, it's required
                telnet_response = connection.read_until(b"\r\n")
                full_banner += telnet_response.rstrip(b"\n")
                if re.match(r"Press 'help' to get a list of all commands. Press 'exit' to end session.", telnet_response):
                    displayed_welcome = True

            if self.show_log_init is True and full_banner != '':
                self.full_banner = full_banner
                logger.info(full_banner)

        except Exception as e:
            log_message = 'trying to authenticate telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        logger.debug("telnet connection established: " + str(connection))
        return connection

    def get_game_preferences(self):
        try:
            connection = self.tn
            connection.write("gg" + b"\r\n")
        except Exception as e:
            log_message = 'trying to getgamepref on telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        telnet_line = ""
        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
                telnet_response += telnet_line
            except Exception as e:
                log_message = 'trying to read_until from telnet connection failed: {}'.format(e)
                raise IOError(log_message)

            m = re.search(r"GamePref.ZombiesRun = (\d{1,2})\r\n", telnet_line)
            if m:
                poll_is_finished = True

        return telnet_response

    def read_line(self):
        try:
            connection = self.tn
            telnet_response = connection.read_very_eager()
            if len(telnet_response) > 0:
                telnet_response_list = telnet_response.splitlines()
                telnet_response_list = [value for value in telnet_response_list if value != ""]
                return telnet_response_list
        except Exception as e:
            log_message = 'trying to read_eager from telnet connection failed: {}'.format(e)
            raise IOError(log_message)

    def listplayers(self):
        try:
            connection = self.tn
            connection.write("lp" + b"\r\n")
        except Exception as e:
            log_message = 'trying to listplayers on telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
                telnet_response += telnet_line
            except Exception as e:
                log_message = 'trying to read_until from telnet connection failed: {}'.format(e)
                raise IOError(log_message)

            m = re.search(r"Total of (\d{1,2}) in the game\r\n", telnet_line)
            if m:
                poll_is_finished = True

        return telnet_response

    def listplayerfriends(self, player_object):
        try:
            connection = self.tn
            connection.write("lpf " + player_object.steamid + b" \r\n")
        except Exception as e:
            log_message = 'trying to listplayerfriends on telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        telnet_response = ""
        friendslist = []
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
                telnet_response += telnet_line
            except Exception as e:
                log_message = 'trying to read_until from telnet connection failed: {}'.format(e)
                raise IOError(log_message)
            m = re.search(r"FriendsOf id=" + str(player_object.steamid) + ", friends=(?P<friendslist>.*)\r\n", telnet_line)
            if m:
                friendslist = m.group("friendslist").split(',')
                poll_is_finished = True

        return friendslist

    def listlandprotection(self):
        try:
            connection = self.tn
            connection.write("llp2" + b"\r\n")
        except Exception as e:
            log_message = 'trying to listlandprotection on telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
                telnet_response += telnet_line
            except Exception as e:
                log_message = 'trying to read_until from telnet connection failed: {}'.format(e)
                raise IOError(log_message)

            m = re.search(r"Total of (\d{1,3}) keystones in the game\r\n", telnet_line)
            if m:
                poll_is_finished = True

        return telnet_response

    def togglechatcommandhide(self, prefix):
        command = "tcch " + prefix + b"\r\n"
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            return False

    def muteplayerchat(self, player_object, flag=True):
        command = "mpc {} {}\r\n".format(player_object.steamid, str(flag).lower())
        if player_object.is_muted == flag: # no sense in double (un)muting someone ^^
            return False

        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            raise IOError

        player_object.set_muted(flag)
        return True

    def kick(self, player_object, reason='just because'):
        command = "kick " + str(player_object.steamid) + " \"" + reason + b"\"\r\n"
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

    def ban(self, player_object, reason='does there always need to be a reason?'):
        command = "ban add " + str(player_object.steamid) + " 1 year \"" + reason.rstrip() + b"\"\r\n"
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

    def unban(self, player_object):
        command = "ban remove " + str(player_object.steamid) + b"\r\n"
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

    def say(self, message, color=None):
        try:
            connection = self.tn
            if color is None:
                color = self.bot.chat_colors['standard']
            telnet_command = "say \"[{}]{}[-]\"\r\n".format(color, str(message))
            connection.write(telnet_command)
        except Exception:
            return False

    def send_message_to_player(self, player_object, message, color=None):
        try:
            connection = self.tn
            if color is None:
                color = self.bot.chat_colors['standard']
            telnet_command = "sayplayer {} \"[{}]{}[-]\"\r\n".format(player_object.steamid, color, str(message))
            connection.write(telnet_command)
        except Exception:
            return False

    def teleportplayer(self, player_object, location_object=None, coord_tuple=None):
        if location_object is not None:
            try:
                coord_tuple = (int(math.ceil(float(location_object.tele_x))), int(math.ceil(float(location_object.tele_y))), int(math.ceil(float(location_object.tele_z))))
            except:
                coord_tuple = (int(math.ceil(float(location_object.pos_x))), int(math.ceil(float(location_object.pos_y))), int(math.ceil(float(location_object.pos_z))))
        else:
            try:
                coord_tuple = (int(math.ceil(float(coord_tuple[0]))), int(math.ceil(float(coord_tuple[1]))), int(math.ceil(float(coord_tuple[2]))))
            except:
                return False

        if player_object.is_responsive() and timeout_occurred(self.bot.listplayers_interval * 2, player_object.last_teleport) and player_object.initialized == True:
            try:
                connection = self.tn
                command = "teleportplayer " + player_object.steamid + " " + str(coord_tuple[0]) + " " + str(coord_tuple[1]) + " " + str(coord_tuple[2])
                logger.info(command)
                connection.write(command + b"\r\n")
                player_object.set_last_teleport()
                return True
            except Exception:
                pass

        return False

    def debuffplayer(self, player_object, buff):
        buff_list = [
            "bleeding",
            "foodPoisoning",
            "brokenLeg",
            "sprainedLeg"
        ]
        if buff not in buff_list:
            return False
        try:
            connection = self.tn
            command = "debuffplayer " + player_object.steamid + " " + str(buff) + "\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def buffplayer(self, player_object, buff):
        buff_list = [
            "firstAidLarge"
        ]
        if buff not in buff_list:
            return False
        try:
            connection = self.tn
            command = "buffplayer " + player_object.steamid + " " + str(buff) + "\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def set_admin_level(self, player_object, level):
        allowed_levels = [
            "2", "4"
        ]
        if level not in allowed_levels:
            return False
        try:
            connection = self.tn
            command = "admin add " + player_object.steamid + " " + str(level) + "\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False
