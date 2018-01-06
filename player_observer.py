from threading import Thread, Event
import re


class PlayerObserver(Thread):
    tn = None
    player = None
    logger = None
    telnet_line = None
    player_name = None

    match_types = None
    actions = None

    def __init__(self, event, logger, player):
        self.logger = logger
        self.player = player
        self.player_name = player["name"]
        Thread.__init__(self)
        self.stopped = event

    def update_telnet_line(self, telnet_line):
        self.telnet_line = telnet_line

    def update_player(self, player):
        self.player = player

    def update_locations(self, locations):
        self.locations = locations

    def run(self):
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            if self.telnet_line is not None:
                print self.telnet_line
                """
                these only have to be run if the telnet is active
                """
                # self.logger.debug(self.telnet_line)
                for match_type in self.match_types:
                    m = re.search(self.match_types[match_type], self.telnet_line)
                    # match chat messages
                    if m:
                        """
                        this is a tricky bit! you need to define all variables used in any action here
                        your IDE will tell you they are not used while in fact they are.
                        the eval down there does the magic ^^
                        so take some time to understand this. or just make it better if you know how ^^
                        """
                        player_name = m.group('player_name')
                        player = self.player
                        locations = self.locations
                        if self.player_name == player_name:
                            command = m.group('command')

                            temp_command = None
                            if self.actions is not None:
                                for action in self.actions:
                                    if action[0] == "isequal":
                                        temp_command = command
                                    if action[0] == "startswith":
                                        temp_command = command.split(' ', 1)[0]

                                    if action[1] == temp_command:
                                        function_name = action[2]
                                        function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                        function_name(*function_parameters)

                self.telnet_line = None

            if self.observers is not None and self.player["is_in_limbo"] is not True:
                """
                these monitor stuff regardless of telnet activity!
                """
                for observer in self.observers:
                    player = self.player
                    locations = self.locations
                    function_name = observer[1]
                    function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                    function_name(*function_parameters)

            self.logger.debug("thread for player " + self.player["name"] + " is active (limbo: " + str(self.player["is_in_limbo"]) + ")")
            next_cycle = 1

        self.stopped.set()
