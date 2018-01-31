import math
import re
import telnetlib

from logger import logger


class TelnetConnection:
    tn = object
    bot = object
    show_log_init = bool

    def __init__(self, ip, port, password, show_log_init=False):
        try:
            connection = telnetlib.Telnet(ip, port, timeout=2)
        except Exception:
            log_message = 'could not establish connection to the host. check ip and port'
            raise IOError(log_message)
        self.show_log_init = show_log_init
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
                logger.info(full_banner)

        except Exception:
            raise

        logger.debug("telnet connection established: " + str(connection))
        return connection

    def read_line(self):
        try:
            connection = self.tn
            telnet_response = connection.read_very_eager()
            if telnet_response and telnet_response != "\r\n":
                return telnet_response.splitlines()
        except Exception:
            raise

    def listplayers(self):
        try:
            connection = self.tn
            connection.write("lp" + b"\r\n")
        except Exception:
            raise

        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            try:
                telnet_response = telnet_response + connection.read_until(b"\r\n")
            except Exception:
                pass

            m = re.search(r"Total of (\d{1,2}) in the game\r\n", telnet_response)
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

    def kick(self, player_object, reason='just because'):
        command = "kick " + str(player_object.steamid) + " \"" + reason + b"\"\r\n"
        try:
            connection = self.tn
            connection.write(command)
        except Exception:
            return False

    def say(self, message):
        message = str(message)
        try:
            connection = self.tn
            telnet_command = "say \"" + message + "\"" + b"\r\n"
            connection.write(telnet_command)
        except Exception:
            return False

        # telnet_response = ""
        # message_got_through = False
        # sanitized_message = re.escape(re.sub(r"\[.*?\]", "", message))
        # timeout = time.time()
        # while message_got_through is not True and not timeout_occurred(2, timeout):
        #     """
        #     fetches the response of the games telnet 'say' command
        #     we are waiting for the games telnet to echo the actual message
        #     """
        #     try:
        #         telnet_response = connection.read_until(b"\r\n")
        #         m = re.search(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + sanitized_message + "\r", telnet_response, re.MULTILINE)
        #         if m:
        #             message_got_through = True
        #     except IndexError:
        #         pass
        # return telnet_response

    def send_message_to_player(self, player_object, message):
        message = str(message)
        try:
            connection = self.tn
            message = "sayplayer " + player_object.steamid + " \"" + message + b"\"\r\n"
            connection.write(message)
        except Exception:
            return False

        # telnet_response = ""
        # message_got_through = False
        # sanitized_message = re.escape(re.sub(r"\[.*?\]", "", message))
        # timeout = time.time()
        # while message_got_through is not True and not timeout_occurred(2, timeout):
        #     """
        #     fetches the response of the games telnet 'say' command
        #     we are waiting for the games telnet to echo the actual message
        #     """
        #     telnet_response = connection.read_until(b"\r\n")
        #     m = re.search(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + sanitized_message + "\r", telnet_response, re.MULTILINE)
        #     if m:
        #         message_got_through = True
        #
        # return telnet_response

    def teleportplayer(self, player_object, location_object):
        if player_object.is_responsive:
            try:
                connection = self.tn
                command = "teleportplayer " + player_object.steamid + " " + str(int(math.ceil(float(location_object.tele_x)))) + " " + str(int(math.ceil(float(location_object.tele_y)))) + " " + str(int(math.ceil(float(location_object.tele_z))))
                logger.info(command)
                connection.write(command + b"\r\n")
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
