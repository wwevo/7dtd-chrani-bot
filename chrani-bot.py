import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import time
from bot.logger import logger
from bot.chrani_bot import ChraniBot
"""
let there be bot:
"""
if __name__ == '__main__':
    while True:
        bot = ChraniBot()
        bot.bot_version = "0.1e"
        try:
            bot.run()
        except (IOError, NameError) as error:
            """ clean up bot to have a clean restart when a new connection can be established """
            try:
                bot.shutdown()  # bot was probably running, restart
                wait_until_reconnect = 20
                log_message = "connection lost, server-restart?"
            except NameError:  # probably started the bot before the server was up
                wait_until_reconnect = 45
                log_message = "can't connect to telnet, is the server running?"
                pass

            log_message = "{} - will try again in {} seconds".format(log_message, str(wait_until_reconnect))
            logger.info(log_message)
            time.sleep(wait_until_reconnect)
            pass

