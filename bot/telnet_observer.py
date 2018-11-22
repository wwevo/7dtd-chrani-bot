import re
from collections import deque
from time import time, sleep
from threading import *
from bot.modules.logger import logger


class TelnetObserver(Thread):
    tn = object
    bot = object
    stopped = object

    run_observer_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float
    recent_telnet_response = str
    valid_telnet_lines = deque

    def __init__(self, event, chrani_bot, telnet_actions):
        self.tn = telnet_actions
        self.bot = chrani_bot
        self.run_observer_interval = 1
        self.last_execution_time = 0.0
        self.valid_telnet_lines = deque()
        self.recent_telnet_response = ""

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        logger.info("telnet observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            if self.bot.is_paused is not False:
                sleep(1)
                continue

            profile_start = time()
            try:
                telnet_response = self.tn.read()
            except:
                self.stopped.set()
                continue

            if len(telnet_response) > 0:
                if len(self.recent_telnet_response) > 0:
                    # adding the remaining lines from last run
                    telnet_response_complete = self.recent_telnet_response + telnet_response
                    self.recent_telnet_response = ""
                    telnet_response = telnet_response_complete

                # the response consists solely of complete line
                telnet_response_list = [value for value in telnet_response.splitlines(True) if value not in ["", b"\r\n"]]
                for telnet_line in telnet_response_list:
                    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})T(\d{2}):(\d{2}):(\d{2})\s(.*)\sINF\s(.*)\r\n", telnet_line)
                    if m:
                        self.valid_telnet_lines.append(telnet_line.rstrip(b"\r\n"))
                    else:
                        self.recent_telnet_response = telnet_line

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("telnet observer thread has stopped")
