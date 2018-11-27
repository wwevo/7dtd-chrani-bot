import math
import re

from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


class TelnetActions:
    tn = object
    bot = object
    last_line = str
    show_log_init = bool

    full_banner = str

    def __init__(self, bot, telnet_connection):
        self.bot = bot
        self.last_line = ""
        self.tn = telnet_connection.tn

    def read(self):
        try:
            connection = self.tn
            telnet_response = connection.read_very_eager()
            return telnet_response
        except Exception as e:
            log_message = 'trying to read_eager from telnet connection failed: {}'.format(e)
            raise IOError(log_message)

    def get_game_preferences(self):
        try:
            connection = self.tn
            connection.write("gg" + b"\r\n")
        except Exception as e:
            log_message = 'trying to getgamepref on telnet connection failed: {}'.format(e)
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

            m = re.search(r"GamePref.ZombiesRun = (\d{1,2})\r\n", telnet_line)
            if m:
                poll_is_finished = True

        game_preferences = re.findall(r"GamePref\.(?P<key>.*)\s=\s(?P<value>.*)\r\n", telnet_response)

        return game_preferences

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

    def gettime(self):
        try:
            connection = self.tn
            connection.write("gt" + b"\r\n")
        except Exception as e:
            log_message = 'trying to get the game time on telnet connection failed: {}'.format(e)
            raise IOError(log_message)

        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
            except Exception as e:
                log_message = 'trying to read_until from telnet connection failed: {}'.format(e)
                raise IOError(log_message)

            m = re.search(r"^Day\s(?P<day>\d{1,5}),\s(?P<hour>\d{1,2}):(?P<minute>\d{1,2}).*\r\n", telnet_line)
            if m:
                poll_is_finished = True
                telnet_response = telnet_line

        return telnet_response

    def listplayerfriends(self, player_object):
        try:
            connection = self.tn
            connection.write("lpf {}".format(player_object.steamid) + b" \r\n")
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
            connection.write("llp" + b"\r\n")
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

        command = "bc-chatprefix {}{}".format(prefix, b"\r\n")
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            return False

    def get_mem_status(self):
        command = b"mem\r\n"
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            return False

        return True
        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_line = connection.read_until(b"\r\n")
            except Exception as e:
                log_message = 'trying to get mem status from telnet connection failed: {}'.format(e)
                raise IOError(log_message)

            m = re.search(self.bot.match_types_system['mem_status'], telnet_line)
            if m:
                telnet_response = telnet_line
                poll_is_finished = True

        return telnet_response

    def muteplayerchat(self, player_object, flag=True):
        command = "mpc {} {}\r\n".format(player_object.steamid, str(flag).lower())
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            raise IOError

        command = "bc-mute {} {}\r\n".format(player_object.steamid, str(flag).lower())
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            raise IOError

        player_object.set_muted(flag)
        return True

    def kick(self, player_object, reason='just because'):
        if not player_object.is_online:
            return True

        command = "kick {} \"{}\"\r\n".format(str(player_object.steamid), reason)
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

    def settime(self, time_string):
        command = "settime {}\r\n".format(str(time_string))
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
        silent_mode = self.bot.settings.get_setting_by_name(name='silent_mode')
        if silent_mode:
            return True
        try:
            connection = self.tn
            if color is None:
                color = self.bot.chat_colors['standard']
            telnet_command = "say \"[{}]{}[-]\"\r\n".format(color, str(message))
            connection.write(telnet_command)
        except Exception:
            return False

    def send_message_to_player(self, player_object, message, color=None):
        silent_mode = self.bot.settings.get_setting_by_name(name='silent_mode')
        if silent_mode:
            return True
        if not player_object.is_online:
            return False

        try:
            connection = self.tn
            if color is None:
                color = self.bot.chat_colors['standard']
            telnet_command = "sayplayer {} \"[{}]{}[-]\"\r\n".format(player_object.steamid, color, str(message))
            connection.write(telnet_command)
        except Exception:
            return False

    def teleportplayer(self, player_object, location_object=None, coord_tuple=None):
        if not player_object.is_online:
            return False

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

        if player_object.is_responsive() and timeout_occurred(self.bot.listplayers_interval * 2, player_object.last_teleport):
            try:
                connection = self.tn
                command = "teleportplayer " + player_object.steamid + " " + str(coord_tuple[0]) + " " + str(coord_tuple[1]) + " " + str(coord_tuple[2])
                logger.info(command)
                connection.write(command + b"\r\n")
                player_object.set_last_teleport()
                player_object.pos_x = coord_tuple[0]
                player_object.pos_y = coord_tuple[1]
                player_object.pos_z = coord_tuple[2]
                self.bot.players.upsert(player_object)

                return True
            except Exception:
                pass

        return False

    def debuffplayer(self, player_object, buff):
        if not player_object.is_online:
            return False

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
        if not player_object.is_online:
            return False

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

    def shutdown(self):
        connection = self.tn
        command = "shutdown\r\n"
        logger.info(command)
        try:
            connection.write(command)
        except Exception:
            return False

    def saveworld(self):
        try:
            connection = self.tn
            command = "saveworld\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def remove_entity(self, entity_id):
        command = "removeentity " + str(entity_id) + b"\r\n"
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

