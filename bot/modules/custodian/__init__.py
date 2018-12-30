import time
from threading import *

from bot.modules.logger import logger


class Custodian(Thread):
    stopped = object

    tn = object
    chrani_bot = object

    run_observer_interval = float
    last_execution_time = float

    health_dict = {
        "main_loop": bool,
        "telnet_observer": bool,
        "webinterface": bool,
        "player_observer": bool,
    }

    def __init__(self, chrani_bot):
        self.chrani_bot = chrani_bot

        self.run_observer_interval = 2
        self.last_execution_time = 0.0

        self.health_dict = {
            "main_loop": False,
            "telnet_observer": False,
            "webinterface": False,
            "player_observer": False,
        }

        Thread.__init__(self)

    def setup(self):
        self.stopped = Event()
        self.name = 'custodian'
        self.isDaemon()
        return self

    def start(self):
        logger.info("chrani custodian started")
        Thread.start(self)
        return self

    def clear_status(self):
        self.health_dict["main_loop"] = False
        self.health_dict["telnet_observer"] = False
        self.health_dict["webinterface"] = False
        self.health_dict["player_observer"] = False

    def check_in(self, observed_entity, status):
        self.health_dict[observed_entity] = status

    def run(self):
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            
            self.chrani_bot.socketio.emit('refresh_health', '', namespace='/chrani-bot/public')

            self.last_execution_time = time.time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time
