"""
next attempt for my bot ^^ this time a bit more organized.

takes command line options like so:
python chrani-bot.py 127.0.0.1 8081 12345678 dummy.sqlite --verbosity=DEBUG
"""
import time

from logger import logger
from command_line_args import args_dict
from telnet_connection import TelnetConnection

from chrani_bot import ChraniBot
"""
let there be bot:
"""
if __name__ == '__main__':
    bot = ChraniBot()
    while True:
        try:
            telnet_connection = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])

            bot.activate()
            bot.setup_telnet_connection(telnet_connection)
            bot.add_match_type({'listplayers_result_regexp': r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\r\n"})
            bot.run()
        except IOError as error:
            """ clean up bot to have a clean restart when a new connection can be established """
            if bot.is_active:
                bot.shutdown()
            wait_until_reconnect = 5
            logger.warn(error)
            log_message = 'will try again in ' + str(wait_until_reconnect) + " seconds"
            logger.info(log_message)
            time.sleep(wait_until_reconnect)
            pass

