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
    recent_telnet_response_has_valid_start = bool
    recent_telnet_response_has_valid_end = bool

    valid_telnet_lines = deque

    def __init__(self, event, chrani_bot, telnet_actions):
        self.tn = telnet_actions
        self.bot = chrani_bot

        self.run_observer_interval = 0.5

        self.recent_telnet_response = None
        self.recent_telnet_response_has_valid_start = False
        self.recent_telnet_response_has_valid_end = False

        self.valid_telnet_lines = deque()
        self.last_execution_time = 0.0

        self.stopped = event
        Thread.__init__(self)

    def is_a_valid_line(self, telnet_line):
        telnet_response_is_a_valid_line = False
        if self.has_valid_start(telnet_line) and self.has_valid_end(telnet_line):
            telnet_response_is_a_valid_line = True

        return telnet_response_is_a_valid_line

    def has_valid_start(self, telnet_response):
        telnet_response_has_valid_start = False
        for match_type in self.bot.match_types_generic["log_start"]:
            if re.match(match_type, telnet_response):
                telnet_response_has_valid_start = True

        return telnet_response_has_valid_start

    def has_valid_end(self, telnet_response):
        telnet_response_has_valid_end = False
        for match_type in self.bot.match_types_generic["log_end"]:
            if re.search(match_type, telnet_response):
                telnet_response_has_valid_end = True

        return telnet_response_has_valid_end

    def has_mutliple_lines(self, telnet_response):
        telnet_response_has_multiple_lines = False
        telnet_response_count = telnet_response.count(b"\r\n")
        if telnet_response_count >= 1:
            telnet_response_has_multiple_lines = telnet_response_count

        return telnet_response_has_multiple_lines

    def get_lines(self, telnet_response):
        telnet_lines_list = [telnet_line for telnet_line in telnet_response.splitlines(True)]
        return telnet_lines_list

    def get_a_bunch_of_lines(self, this_many_lines):
        telnet_lines = []
        current_queue_length = 0
        done = False
        while (current_queue_length < this_many_lines) and not done:
            try:
                telnet_lines.append(self.valid_telnet_lines.popleft())
                current_queue_length += 1
            except IndexError:
                done = True

        if len(telnet_lines) >= 1:
            return telnet_lines
        else:
            return False

    def run(self):
        logger.info("telnet observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            self.bot.custodian.check_in('telnet_observer', True)

            if not self.bot.has_connection:
                raise IOError("{source}/{error_message}".format(source="telnet observer", error_message="lost telnet connection :("))

            if self.bot.is_paused is not False:
                sleep(1)
                continue

            profile_start = time()

            try:
                telnet_response = self.tn.read_very_eager()
                # print(telnet_response)
            except:
                self.stopped.set()
                continue

            if len(telnet_response) > 0:
                processing_done = False
                """ telnet returned data. let's get some information about it"""
                response_count = 1
                telnet_response_components = self.get_lines(telnet_response)
                for component in telnet_response_components:
                    if self.is_a_valid_line(component):
                        self.valid_telnet_lines.append(component.rstrip(b"\r\n"))
                        # logger.debug("{error_message}/{telnet_line}".format(error_message="added complete line: ", telnet_line=component.rstrip(b"\r\n")))
                    else:
                        if response_count == 1:
                            # not a complete line, but the first in the list: might be the rest of last run
                            if self.recent_telnet_response is not None:
                                combined_line = "{}{}".format(self.recent_telnet_response, component)
                                if self.is_a_valid_line(combined_line):
                                    self.valid_telnet_lines.append(combined_line.rstrip(b"\r\n"))
                                    # logger.debug("{error_message}/{telnet_line}".format(error_message="added complete combined line: ", telnet_line=combined_line.rstrip(b"\r\n")))
                                else:
                                    # logger.debug("{error_message}/{telnet_line}".format(error_message="combined line, it doesnt make sense though: ", telnet_line=combined_line.rstrip(b"\r\n")))
                                    pass

                                self.recent_telnet_response = None
                            else:
                                if len(telnet_response_components) == 1:
                                    if self.has_valid_start(component):
                                        # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line, storing for next run: ", telnet_line=component.rstrip(b"\r\n")))
                                        self.recent_telnet_response = component
                                    else:
                                        # logger.debug("{error_message}/{telnet_line}".format(error_message="what happened?: ", telnet_line=component.rstrip(b"\r\n")))
                                        pass

                        elif response_count == len(telnet_response_components):
                            # not a complete line, but the last in the list: might be the beginning of next run
                            if self.has_valid_start(component):
                                self.recent_telnet_response = component
                                # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line, storing for next run: ", telnet_line=component.rstrip(b"\r\n")))
                            else:
                                # logger.debug("{error_message}/{telnet_line}".format(error_message="does not seem to be usable: ", telnet_line=component.rstrip(b"\r\n")))
                                pass

                        else:
                            # not a complete line right in the middle. We don't need this!!
                            # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line smack in the middle: ", telnet_line=component.rstrip(b"\r\n")))
                            pass

                    response_count += 1

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("telnet observer thread has stopped")
