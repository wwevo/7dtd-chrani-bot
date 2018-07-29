from urllib import urlencode
import flask
import flask_login
import re
from bot.modules.logger import logger
from threading import *


class Webinterface(Thread):
    bot = object
    app = object

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        pass
