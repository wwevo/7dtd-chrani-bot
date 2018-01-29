"""
set up and maintain the telnet connection to the game-server
"""
import telnetlib
import re
import atexit
import time
import math
from logger import logger
from timeout import timeout_occurred


class TelnetConnection:
    connection = object
    logger = object
    ip = str
    port = str
    password = str

    telnet_response = str

    def __init__(self, ip, port, password):
        """

        :param ip:
        :param port:
        :param password:
        """
        self.logger = logger
        self.ip = ip
        self.port = port
        self.password = password
        self.telnet_response = ""
        # TODO : instead of arguments you could use the attribute defined earlier for the method bellow
        self.__get_telnet_connection(ip, port, password)
        atexit.register(self.__cleanup)

    def __cleanup(self):
        """
        Clean up the connection.
        :return:
        """
        # TODO method could be replace by __exit__ instead of using atexit
        # i have tried it with __exit__ it never got called. ever. in any class. thats why i got atexit in the first place
        if self.connection is not None:
            self.connection.close()
            self.logger.debug("telnet connection closed: " + str(self.connection))

    def __get_telnet_connection(self, ip, port, password):
        """
        Connect to server.
        :param ip: (str) IP of the server
        :param port: (str) port of the server
        :param password: (str) password of the server
        :return:
        """
        try:
            connection = telnetlib.Telnet(ip, port, timeout=2)
            self.connection = connection
        except Exception:
            log_message = 'could not establish connection to the host. check ip and port'
            # this seems to be logged automatically oO
            # self.logger.critical(log_message)
            raise IOError(log_message)

        try:
            # Waiting for the prompt.
            found_prompt = False
            while found_prompt is not True:
                telnet_response = connection.read_until(b"\r\n")
                if re.match(r"Please enter password:\r\n", telnet_response):
                    found_prompt = True

            # Sending password.
            connection.write(password.encode('ascii') + b"\r\n")
            authenticated = False
            while authenticated is not True:
                telnet_response = connection.read_until(b"\r\n")  # read line by line
                # last 'welcome' line from the games telnet. it might change with a new game-version
                if re.match(r"Password incorrect, please enter password:\r\n", telnet_response) is not None:
                    log_message = 'incorrect telnet password'
                    self.logger.critical(log_message)
                    raise ValueError()
                if re.match(r"Logon successful.\r\n", telnet_response) is not None:
                    authenticated = True
                    self.logger.debug(telnet_response)

            # Waiting for banner.
            displayed_welcome = False
            while displayed_welcome is not True:
                telnet_response = connection.read_until(b"\r\n")  # read everything it has to give
                if re.match(r"Press 'help' to get a list of all commands. Press 'exit' to end session.", telnet_response):
                    displayed_welcome = True
                    self.logger.debug(telnet_response)

        except Exception:
            raise

        self.logger.debug("telnet connection established: " + str(connection))
        return connection

    def read_line(self, message=b"\r\n"):
        try:
            connection = self.connection
            telnet_response = connection.read_very_eager()
            if telnet_response and telnet_response != "\r\n":
                return telnet_response.splitlines()
        except Exception:
            raise

    def listplayers(self):
        """
        List player online
        :return:
        """
        try:
            connection = self.connection
            connection.write("lp" + b"\r\n")
        except Exception:
            raise

        player_count = 0
        telnet_response = ""
        poll_is_finished = False
        timeout_start = time.time()
        timeout_after_n_seconds = 2
        while poll_is_finished is not True and not timeout_occurred(timeout_after_n_seconds, timeout_start):
            """
            fetches the response of the games telnet 'lp' command
            (lp = list players)
            last line from the games lp command, the one we are matching,
            might change with a new game-version
            returns 
            the complete response and
            the playercount
            """
            try:
                telnet_response = telnet_response + connection.read_until(b"\r\n")
                # if telnet_response:
                #     self.logger.debug(telnet_response)
            except Exception:
                pass

            m = re.search(r"Total of (\d{1,2}) in the game\r\n", telnet_response)
            if m:
                player_count = m.group(1)
                poll_is_finished = True

        return telnet_response, player_count

    def togglechatcommandhide(self, prefix):
        command = "tcch " + prefix + b"\r\n"
        try:
            connection = self.connection
            connection.write(command)
        except:
            return False

    def kick(self, player_object, reason='just because'):
        command = "kick " + player_object.name + " \"" + reason + b"\"\r\n"
        try:
            connection = self.connection
            connection.write(command)
        except:
            return False

    def say(self, message):
        """
        Say something on the chat.
        :param message: (str) message to send
        :return: bool for success
        """
        message = str(message)
        try:
            connection = self.connection
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
        """
        Say something on the chat.
        :param player_object: (Player) receiver of the message
        :param sender_name: (str) name that should be given as sender
        :param message: (str) message to send
        :return: bool for success
        """
        message = str(message)
        try:
            connection = self.connection
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
        """
        Teleport a player to some coords.
        :param player_object: player
        :param location_object: coordinate
        :return: bool for success
        """
        # current_time = time.time()
        # last_teleport = player_object.last_teleport
        # diff = current_time - last_teleport
        # if player_object.last_teleport is not None and (current_time - int(player_object.last_teleport)) < 2:
        #     self.logger.debug(time.time() - player_object.last_teleport)
        #     return False
        if player_object.is_responsive:
            try:
                connection = self.connection
                command = "teleportplayer " + player_object.steamid + " " + str(int(math.ceil(float(location_object.tele_x)))) + " " + str(int(math.ceil(float(location_object.tele_y)))) + " " + str(int(math.ceil(float(location_object.tele_z)))) + b"\r\n"
                self.logger.info(command)
                # player_object.last_teleport = time.time()
                connection.write(command)
                # player_object.switch_off("telnet")
            except Exception:
                return False
        # try:
        #     teleport_succeeded = False
        #     timeout = time.time()
        #     while teleport_succeeded is not True and not timeout_occurred(2, timeout):
        #         telnet_response = connection.read_until(b"\r\n")
        #         m = re.search(self.bot.match_types_system["telnet_events_playerspawn"], telnet_response)
        #         if m:
        #             if m.group("command") == "Teleport":
        #                 if player_object.name == m.group("player_name"):
        #                     player_object.last_teleport = time.time()
        #                     teleport_succeeded = True
        # except Exception:
        #     return False

        return True

    def debuffplayer(self, player_object, buff):
        """
        issues a debuff for a player
        :param player_object: player
        :buff the buff to be removed
        :return:
        """
        debuff_list = [
            "bleeding",
            "foodPoisoning",
            "brokenLeg",
            "sprainedLeg"
        ]
        if buff not in debuff_list:
            return False
        try:
            connection = self.connection
            command = "debuffplayer " + player_object.steamid + " " + str(buff) + "\r\n"
            self.logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def buffplayer(self, player_object, buff):
        """
        issues a debuff for a player
        :param player_object: player
        :buff the buff to be removed
        :return:
        """
        buff_list = [
            "firstAidLarge"
        ]
        if buff not in buff_list:
            return False
        try:
            connection = self.connection
            command = "buffplayer " + player_object.steamid + " " + str(buff) + "\r\n"
            self.logger.info(command)
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
            connection = self.connection
            command = "add admin " + player_object.steamid + " " + str(level) + "\r\n"
            self.logger.info(command)
            connection.write(command)
        except Exception:
            return False
