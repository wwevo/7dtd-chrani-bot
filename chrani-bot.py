""" takes command line options like so:
python chrani-bot.py 127.0.0.1 8081 12345678 local --verbosity=DEBUG
nohup python chrani-bot.py 127.0.0.1 8081 12345678 local --verbosity=DEBUG > /dev/null 2>&1 &
"""
import time
from bot.logger import logger
from bot.chrani_bot import ChraniBot
"""
let there be bot:
"""
if __name__ == '__main__':
    while True:
        try:
            bot = ChraniBot()  # leaving this here while we have no database so the location data (lobby, base etc.) is kept in memory
            bot.run()
        except IOError as error:
            """ clean up bot to have a clean restart when a new connection can be established """
            if bot.is_active:
                bot.shutdown()
            wait_until_reconnect = 5
            logger.warn(error)
            log_message = "will try again in {} seconds".format(str(wait_until_reconnect))
            logger.info(log_message)
            time.sleep(wait_until_reconnect)
            pass

