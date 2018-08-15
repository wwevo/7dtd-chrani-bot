import os
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

import sys
import time
from bot.modules.logger import logger
from bot.chrani_bot import ChraniBot

import multiprocessing

try:
    import gunicorn.app.base
    from gunicorn.six import iteritems
    we_are_local = False


    def number_of_workers():
        return (multiprocessing.cpu_count() * 2) + 1


    def handler_app(environ, start_response):
        response_body = b'Works fine'
        status = '200 OK'

        response_headers = [
            ('Content-Type', 'text/plain'),
        ]

        start_response(status, response_headers)

        return [response_body]


    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            config = dict([(key, value) for key, value in iteritems(self.options)
                           if key in self.cfg.settings and value is not None])
            for key, value in iteritems(config):
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

except ImportError:
    we_are_local = True
    pass


"""
let there be bot:
"""
if __name__ == '__main__':
    while True:
        try:
            bot = ChraniBot()
            bot.app_root = root_dir
            bot.bot_version = "0.5b"
            if we_are_local:
                bot.run()
            else:
                options = {
                    'bind': '%s:%s' % ('127.0.0.1', '5000'),
                    'workers': number_of_workers(),
    }
                StandaloneApplication(bot, options).run()
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
