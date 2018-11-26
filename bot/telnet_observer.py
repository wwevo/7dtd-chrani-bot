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
        self.run_observer_interval = 0.8
        self.last_execution_time = 0.0
        self.valid_telnet_lines = deque()
        self.recent_telnet_response = ""

        self.stopped = event
        Thread.__init__(self)

    def has_valid_start(self, telnet_response):
        telnet_response_has_valid_start = False
        for match_type in self.bot.match_types_generic["log_start"]:
            if re.match(match_type, telnet_response):
                telnet_response_has_valid_start = True
                break

        return telnet_response_has_valid_start

    def has_valid_end(self, telnet_response):
        telnet_response_has_valid_end = False
        for match_type in self.bot.match_types_generic["log_end"]:
            if re.search(match_type, telnet_response):
                telnet_response_has_valid_end = True
                break

        return telnet_response_has_valid_end

    def has_mutliple_lines(self, telnet_response):
        telnet_response_has_multiple_lines = False
        telnet_response_count = telnet_response.count(b"\r\n")
        if telnet_response_count > 1:
            telnet_response_has_multiple_lines = telnet_response_count

        return telnet_response_has_multiple_lines

    def run(self):
        logger.info("telnet observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            if not self.bot.has_connection:
                raise IOError

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
                # telnet returned data!!
                telnet_response_has_valid_start = self.has_valid_start(telnet_response)
                telnet_response_has_valid_end = self.has_valid_end(telnet_response)

                if len(self.recent_telnet_response) > 0:
                    # got something in the buffer!!
                    if telnet_response_has_valid_start:
                        self.valid_telnet_lines.append(self.recent_telnet_response.rstrip(b"\r\n"))
                        self.recent_telnet_response = ""
                    elif telnet_response_has_valid_end:
                        # got no start, but got an end!! add it to the buffer
                        telnet_response = "{}{}".format(self.recent_telnet_response, telnet_response)
                        telnet_response_has_valid_start = self.has_valid_start(telnet_response)
                        telnet_response_has_valid_end = self.has_valid_end(telnet_response)
                        self.recent_telnet_response = ""

                if telnet_response_has_valid_start and telnet_response_has_valid_end:
                    # this is a done deal, it starts and ends with the proper stuff, we can just hack it up as a list
                    telnet_response_list = [value for value in telnet_response.splitlines(True)]
                    for telnet_line in telnet_response_list:
                        # and store each individual line in the global queue
                        if self.has_valid_start(telnet_line) and self.has_valid_end(telnet_line):
                            self.valid_telnet_lines.append(telnet_line.rstrip(b"\r\n"))
                    continue

                if telnet_response_has_valid_start and not telnet_response_has_valid_end:
                    # we have a start, no valid end
                    telnet_response_list = [value for value in telnet_response.splitlines(True)]
                    if len(telnet_response_list) > 0:
                        # we have more than one line, store those and safe the remainder for next run
                        self.recent_telnet_response = telnet_response_list.pop()

                        for telnet_line in telnet_response_list:
                            # and store each individual line in the global queue
                            if self.has_valid_start(telnet_line) and self.has_valid_end(telnet_line):
                                self.valid_telnet_lines.append(telnet_line.rstrip(b"\r\n"))
                        continue

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("telnet observer thread has stopped")
