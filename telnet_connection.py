"""
set up and maintain the telnet connection to the game-server
"""
import telnetlib
import re
import atexit
import time

class TelnetConnection:
    connection = None
    logger = None
    ip = None
    port = None
    password = None

    def __init__(self, logger, ip, port, password):
        self.logger = logger
        self.ip = ip
        self.port = port
        self.password = password
        self.connection = self.__get_telnet_connection(ip, port, password)
        atexit.register(self.__cleanup)

    def keep_alive(self):
        ip = self.ip
        port = self.port
        password = self.password
        self.connection = self.__get_telnet_connection(ip, port, password)

    def __cleanup(self):
        if self.connection is not None:
            self.connection.close()
            self.logger.debug("telnet connection closed: " + str(self.connection))

    def __get_telnet_connection(self, ip, port, password):
        try:
            try:
                connection = telnetlib.Telnet(ip, port)
            except Exception:
                log_message = 'could not establish connection to the host. check ip and port'
                # this seems to be logged automatically oO
                # self.logger.critical(log_message)
                raise IOError(log_message)

            try:
                found_prompt = False
                while found_prompt is not True:
                    telnet_response = connection.read_until(b"\r\n")  # read everything it has to give
                    if re.match(r"Please enter password:\r\n", telnet_response):
                        found_prompt = True

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
            except Exception:
                raise

        except Exception:
            raise

        self.logger.debug("telnet connection established: " + str(connection))
        return connection

    def read_line(self, message):
        try:
            connection = self.connection
            telnet_response = connection.read_until(b"\r\n", 2)
            if telnet_response:
                self.logger.debug(telnet_response)
        except Exception:
            raise

        return telnet_response

    def listplayers(self):
        try:
            connection = self.connection
            connection.write("lp" + b"\r\n")
        except Exception:
            log_message = 'could not establish connection to the host. check ip and port'
            # this seems to be logged automatically oO
            # self.logger.critical(log_message)
            raise IOError(log_message)

        player_count = 0
        telnet_response = ""
        poll_is_finished = False
        while poll_is_finished is not True:
            """
            fetches the response of the games telnet 'lp' command
            (lp = list players)
            last line from the games lp command, the one we are matching,
            might change with a new game-version
            returns 
            the complete response and
            the playercount
            """
            telnet_response = telnet_response + connection.read_eager()

            m = re.search(r"Total of (\d{1,2}) in the game\r\n", telnet_response)
            if m:
                player_count = m.group(1)
                poll_is_finished = True

        return telnet_response, player_count

    def say(self, message):
        try:
            connection = self.connection
            connection.write("say \"" + message + b"\"\r\n")
        except Exception:
            return False

        telnet_response = ""
        message_got_through = False
        sanitized_message = re.escape(re.sub(r"\[.*?\]", "", message))
        while message_got_through is not True:
            """
            fetches the response of the games telnet 'say' command
            we are waiting for the games telnet to echo the actual message
            """
            telnet_response = telnet_response + connection.read_very_eager()
            m = re.search(r"(.+?) (.+?) INF Chat: \'.*\':.* " + sanitized_message + "\r", telnet_response)
            if m:
                message_got_through = True

        return telnet_response

    def teleportplayer(self, player, location):
        try:
            connection = self.connection
            while True:
                if player["is_in_limbo"] is not True:
                    connection.write(
                        "teleportplayer " + player["steamid"] + " " + str(int(float(location["pos_x"]))) + " " + str(
                            int(float(location["pos_y"]))) + " " + str(int(float(location["pos_z"]))) + b"\r\n")
                    break
                else:
                    time.sleep(0.5)
        except:
            return False

