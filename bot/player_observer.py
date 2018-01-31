from command_line_args import args_dict
from telnet_connection import TelnetConnection
from timeout import timeout_occurred
from threading import Thread, Event
from logger import logger

import time, re


class PlayerObserver(Thread):
    tn = object
    bot = object
    logger = object
    run_observers_interval = int  # loop this every run_observers_interval seconds

    player_steamid = str

    def __init__(self, bot, event, player_steamid):
        self.player_steamid = str(player_steamid)
        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.bot = bot
        self.run_observers_interval = 1

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        self.tn.send_message_to_player(self.bot.players.players_dict[self.player_steamid], "{} is ready and listening".format(self.bot.name))

        player_object = self.bot.players.get(self.player_steamid)

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()

            if self.bot.observers:
                if player_object.is_responsive:
                    """ execute real-time observers
                    these are run regardless of telnet activity!
                    """
                    command_queue = []
                    for observer in self.bot.observers:
                        function_name = observer[1]
                        function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                        command_queue.append([function_name, function_parameters])
                    for command in command_queue:
                        if player_object.is_responsive:
                            try:
                                command[0](*command[1])
                            except TypeError:
                                command[0](command[1])
                        else:
                            break
                else:
                    if player_object.has_health():
                        player_object.switch_on("caught you alive and kickin'")

                execution_time = time.time() - profile_start
                next_cycle = self.run_observers_interval - execution_time
        logger.debug("thread has stopped")

    def trigger_action(self, telnet_line):
        current_telnet_line = telnet_line

        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], current_telnet_line)
            if m:
                player_name = m.group('player_name')
                for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                    if player_object.name == player_name:
                        player_object = self.bot.players.players_dict[player_steamid]

                        command = m.group('command')
                        if self.bot.player_actions is not None:
                            for action in self.bot.player_actions:
                                if player_object.is_responsive:
                                    if (action[0] == "isequal" and action[1] == command) or (action[0] == "startswith" and command.startswith(action[1])):
                                        function_name = action[2]
                                        function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                        try:
                                            function_name(*function_parameters)
                                        except TypeError:
                                            function_name(function_parameters)
                                else:
                                    break

                        break
