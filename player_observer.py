from threading import Thread, Event


class PlayerObserver(Thread):
    player = None
    logger = None
    global_telnet_line = None

    def __init__(self, event, logger, player, global_telnet_line):
        self.player = player
        self.logger = logger
        self.global_telnet_line = global_telnet_line
        Thread.__init__(self)
        self.stopped = event

    def update_telnet_line(self, telnet_line):
        self.global_telnet_line = telnet_line

    def run(self):
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            self.logger.info(self.global_telnet_line)
            self.logger.debug("thread for player " + self.player["name"] + " is active (limbo: " + str(self.player["is_in_limbo"]) + ")")
            next_cycle = 2

        self.stopped.set()
