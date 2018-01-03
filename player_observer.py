from threading import Thread, Event
import re


class PlayerObserver(Thread):
    tn = None
    player = None
    logger = None
    global_telnet_line = None

    match_types = None
    actions = None

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
            for match_type in self.match_types:
                m = re.search(self.match_types[match_type], self.global_telnet_line)
                # match chat messages
                if m:
                    player_name = m.group('player_name')
                    player = self.player
                    command = m.group('command')

                    temp_command = None
                    if self.actions is not None:
                        for action in self.actions:
                            if action[0] == "isequal":
                                temp_command = command
                            if action[0] == "startswith":
                                temp_command = command.split(' ', 1)[0]

                            if action[1] == temp_command:
                                print "action"
                                #  function_matchtype = action[0]
                                function_name = action[2]
                                function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                function_name(*function_parameters)

            self.logger.debug("thread for player " + self.player["name"] + " is active (limbo: " + str(self.player["is_in_limbo"]) + ")")
            next_cycle = 2

        self.stopped.set()
