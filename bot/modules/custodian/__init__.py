import time
from threading import *

from bot.modules.logger import logger


class Custodian(Thread):
    tn = object
    bot = object

    health_dict = {
        "main_loop": bool,
        "telnet_observer": bool,
        "webinterface": bool,
        "player_observers": bool,
    }

    def __init__(self, event, chrani_bot):
        self.bot = chrani_bot

        self.run_observer_interval = 5
        self.last_execution_time = 0.0

        self.clear_env()
        self.stopped = event
        Thread.__init__(self)

    def clear_env(self):
        self.health_dict = {
            "main_loop": False,
            "telnet_observer": False,
            "webinterface": False,
            "player_observers": False,
        }

    def check_in(self, observed_entity, status):
        self.health_dict[observed_entity] = status

    def run(self):
        logger.info("chrani custodian started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            
            self.bot.socketio.emit('refresh_health', '', namespace='/chrani-bot/public')

            self.last_execution_time = time.time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time