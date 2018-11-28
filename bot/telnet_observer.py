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

        self.run_observer_interval = 0.8

        self.recent_telnet_response = None
        self.recent_telnet_response_has_valid_start = False
        self.recent_telnet_response_has_valid_end = False

        self.valid_telnet_lines = deque()
        self.last_execution_time = 0.0

        self.stopped = event
        Thread.__init__(self)

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
        if telnet_response_count > 1:
            telnet_response_has_multiple_lines = telnet_response_count

        return telnet_response_has_multiple_lines

    def run(self):
        logger.info("telnet observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            if not self.bot.has_connection:
                raise IOError("{source}/{error_message}".format(source="telnet observer", error_message="lost telnet connection :("))

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
                processing_done = False
                """ telnet returned data. let's get some information about it"""
                telnet_response_has_valid_start = self.has_valid_start(telnet_response)
                telnet_response_has_valid_end = self.has_valid_end(telnet_response)
                telnet_response_has_multiple_lines = self.has_mutliple_lines(telnet_response)

                if not processing_done and telnet_response_has_valid_start and telnet_response_has_valid_end and not telnet_response_has_multiple_lines:
                    # (1) simplest case: correct start, correct end, and just the one line
                    self.valid_telnet_lines.append(telnet_response.rstrip(b"\r\n"))

                    self.recent_telnet_response = None
                    self.recent_telnet_response_has_valid_start = False
                    self.recent_telnet_response_has_valid_end = False
                    processing_done = True

                if not processing_done and telnet_response_has_valid_start and telnet_response_has_valid_end and telnet_response_has_multiple_lines:
                    # (2) second simplest case ^^: correct start, correct end, but several lines.
                    # we split 'em up and check if they are complete lines, otherwise discard them as irrelevant output
                    telnet_lines_list = [telnet_line for telnet_line in telnet_response.splitlines(True)]
                    for telnet_line in telnet_lines_list:
                        telnet_line_has_valid_start = self.has_valid_start(telnet_line)
                        telnet_line_has_valid_end = self.has_valid_end(telnet_line)
                        if telnet_line_has_valid_start and telnet_line_has_valid_end:
                            self.valid_telnet_lines.append(telnet_line.rstrip(b"\r\n"))
                        else:
                            if not re.match(r"(\A\sid=\d+$)|(\AObservers$)", telnet_line.rstrip(b"\r\n")):
                                logger.debug("{source}/{error_message}/{discarded_telnet_line}".format(source="telnet observer", error_message="discard (2)", discarded_telnet_line=telnet_line.rstrip(b"\r\n")))

                    self.recent_telnet_response = None
                    self.recent_telnet_response_has_valid_start = False
                    self.recent_telnet_response_has_valid_end = False
                    processing_done = True

                if not processing_done and telnet_response_has_valid_start and not telnet_response_has_valid_end and not telnet_response_has_multiple_lines:
                    # (3) multipart case: we have the start in order, the end seems to be missing though
                    # it's just one line, so it probably didn't get completely sent yet. store it for next poll!
                    self.recent_telnet_response = telnet_response
                    self.recent_telnet_response_has_valid_start = telnet_response_has_valid_start
                    self.recent_telnet_response_has_valid_end = telnet_response_has_valid_end
                    processing_done = True

                if not processing_done and telnet_response_has_multiple_lines:
                    # (4) multipart case: we have the start in order, the end seems to be missing - there seem to be several lines though
                    # let's check them out and store the incomplete lines for next run,
                    # discard all incompletes when a complete one is found as irrelevant
                    incomplete_line_count = 0
                    telnet_lines_list = [telnet_line for telnet_line in telnet_response.splitlines(True)]
                    for telnet_line in telnet_lines_list:
                        # this is similar to the previous stuff, we do not need to check for multiple lines though, since we split the shit up!
                        # we simply discard incomplete lines, unless they are a legitimate start, then we store it for later (should always ever only be the last one)
                        telnet_line_has_valid_start = self.has_valid_start(telnet_line)
                        telnet_line_has_valid_end = self.has_valid_end(telnet_line)

                        if telnet_line_has_valid_start and telnet_line_has_valid_end and self.recent_telnet_response is not None:
                            # line is fine. but there's something in the buffer. can't match it. gone with it!!!
                            logger.debug("{source}/{error_message}/{discarded_incomplete_telnet_line}".format(source="telnet observer", error_message="discarded incomplete line", discarded_incomplete_telnet_line=self.recent_telnet_response.rstrip(b"\r\n")))

                            self.recent_telnet_response = None
                            self.recent_telnet_response_has_valid_start = False
                            self.recent_telnet_response_has_valid_end = False

                        if telnet_line_has_valid_start and telnet_line_has_valid_end and self.recent_telnet_response is None:
                            # perfectly fine line. we'll take it!
                            self.valid_telnet_lines.append(telnet_line.rstrip(b"\r\n"))
                            continue

                        if not telnet_line_has_valid_start and telnet_line_has_valid_end and self.recent_telnet_response is not None:
                            combined_telnet_response = "{recent_telnet_response}{telnet_response}".format(recent_telnet_response=self.recent_telnet_response, telnet_response=telnet_response)
                            combined_telnet_response_has_valid_start = self.has_valid_start(combined_telnet_response)
                            combined_telnet_response_has_valid_end = self.has_valid_end(combined_telnet_response)
                            if combined_telnet_response_has_valid_start and combined_telnet_response_has_valid_end:
                                self.valid_telnet_lines.append(combined_telnet_response.rstrip(b"\r\n"))
                                logger.debug("/{error_message}/{telnet_line}".format(source="telnet observer", error_message="added incomplete line (1)", telnet_line=combined_telnet_response.rstrip(b"\r\n")))
                                self.recent_telnet_response = None
                                self.recent_telnet_response_has_valid_start = False
                                self.recent_telnet_response_has_valid_end = False

                        if telnet_line_has_valid_start and not telnet_line_has_valid_end:
                            logger.debug("/{error_message}/{telnet_line}".format(source="telnet observer", error_message="saved incomplete line", telnet_line=telnet_line.rstrip(b"\r\n")))
                            self.recent_telnet_response = telnet_line
                            self.recent_telnet_response_has_valid_start = telnet_line_has_valid_start
                            self.recent_telnet_response_has_valid_end = telnet_line_has_valid_end
                            incomplete_line_count += 1

                    processing_done = True
                    if incomplete_line_count > 1:
                        # just for debugging. it should never be greater than one if my logic is sound *g*
                        print(incomplete_line_count)

                if not processing_done and not telnet_response_has_multiple_lines:
                    combined_telnet_response = "{recent_telnet_response}{telnet_response}".format(recent_telnet_response=self.recent_telnet_response, telnet_response=telnet_response)
                    combined_telnet_response_has_valid_start = self.has_valid_start(combined_telnet_response)
                    combined_telnet_response_has_valid_end = self.has_valid_end(combined_telnet_response)
                    if combined_telnet_response_has_valid_start and combined_telnet_response_has_valid_end:
                        self.valid_telnet_lines.append(combined_telnet_response.rstrip(b"\r\n"))
                        logger.debug("/{error_message}/{telnet_line}".format(source="telnet observer", error_message="added incomplete line (2)", telnet_line=combined_telnet_response.rstrip(b"\r\n")))
                        self.recent_telnet_response = None
                        self.recent_telnet_response_has_valid_start = False
                        self.recent_telnet_response_has_valid_end = False
                        processing_done = True

                if not processing_done:
                    logger.debug("/{error_message}/{telnet_line}".format(source="telnet observer", error_message="nothing was done with this line oO", telnet_line=telnet_response.rstrip(b"\r\n")))

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("telnet observer thread has stopped")
