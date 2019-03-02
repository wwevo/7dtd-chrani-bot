import re
import telnetlib

from bot.modules.logger import logger


class Telnet:
    authenticated_connection = object
    show_log_init = bool

    def __init__(self, ip, port, password, show_log_init=False):
        try:
            connection = telnetlib.Telnet(ip, port, timeout=3)
        except Exception as e:
            log_message = 'trying to establish telnet connection failed: {}'.format(e)
            # logger.error(log_message)
            raise IOError(log_message)

        self.show_log_init = show_log_init

        try:
            self.authenticated_connection = self.authenticate(connection, password)
        except IOError:
            raise

    def authenticate(self, connection, password):
        try:
            # Waiting for the prompt.
            found_prompt = False
            while found_prompt is not True:
                telnet_response = connection.read_until(b"\r\n", timeout=3)
                if re.match(r"Please enter password:\r\n", telnet_response):
                    found_prompt = True
                else:
                    log_message = 'telnet connection timed out'
                    logger.critical(log_message)
                    raise IOError(log_message)

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

        except Exception as e:
            log_message = 'trying to authenticate telnet connection failed: {}'.format(e)
            # logger.error(log_message)
            raise IOError(log_message)

        logger.debug("telnet connection established: " + str(connection))
        return connection

    def read_very_eager(self):
        try:
            return self.connection.read_very_eager()
        except Exception as e:
            log_message = 'trying to read_very_eager from telnet connection failed: {} / {}'.format(e, type(e))
            # logger.error(log_message)
            raise IOError(log_message)

