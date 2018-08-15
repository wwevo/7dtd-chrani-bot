import os
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

import sys
import time
from bot.modules.logger import logger
from bot.chrani_bot import ChraniBot
from threading import *
from bot.modules.webinterface.webinterface import Webinterface

webinterface = object


def load_webinterface():
    global webinterface
    webinterface_thread_stop_flag = Event()
    webinterface_thread = Webinterface(webinterface_thread_stop_flag)  # I'm passing the bot (self) into it to have easy access to it's variables
    webinterface_thread.name = "webinterface"  # nice to have for the logs
    webinterface_thread.isDaemon()
    webinterface_thread.start()
    webinterface = webinterface_thread
    return webinterface_thread.app


"""
let there be bot:
"""
if __name__ == '__main__':
    while True:
        try:
            bot = ChraniBot()
            bot.app_root = root_dir
            bot.bot_version = "0.5b"
            load_webinterface()
            bot.webinterface = webinterface
            bot.webinterface.bot = bot
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
            # logger.exception(log_message)
            time.sleep(wait_until_reconnect)
            pass

        try:
            if bot.is_active is False:
                sys.exit()
        except NameError:
            pass
