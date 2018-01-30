from command_line_args import args_dict
from telnet_connection import TelnetConnection
from timeout import timeout_occurred

from threading import Thread, Event
from logger import logger
import time
import re


class PlayerObserver(Thread):
    tn = object
    bot = object
    logger = object

    player_steamid = str

    run_observers_interval = int  # loop this every run_observers_interval seconds


    def __init__(self, bot, event, player_steamid):
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.bot = bot
        self.run_observers_interval = 1
        self.player_steamid = str(player_steamid)

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0

        log_status_interval = 1  # print player status ever ten seconds or so
        log_status_start = 0
        log_status_timeout = 0  # should log first, then timeout ^^

        self.tn.send_message_to_player(self.bot.players.players_dict[self.player_steamid], "bot " + self.bot.name + " is ready and listening")

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            player = self.bot.players.get(self.player_steamid)

            if self.bot.observers and player.is_alive():
                """ execute real-time observers
                these are run regardless of telnet activity!
                """
                command_queue = []
                for observer in self.bot.observers:
                    function_name = observer[1]
                    function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                    command_queue.append([function_name, function_parameters])
                for command in command_queue:
                    if player.is_alive():
                        try:
                            command[0](*command[1])
                        except TypeError:
                            command[0](command[1])
                    else:
                        break

                execution_time = time.time() - profile_start
                next_cycle = self.run_observers_interval - execution_time

                if time.time() - log_status_start > log_status_timeout:
                    """ prepare log-output
    
                    so we don't have it clogged with endless meaningless lines
                    """
                    log_message = "executed player_observer loop. that took me like totally less than {} seconds!!".format(execution_time)
                    logger.debug(log_message)

                    log_status_start = time.time()
                    log_status_timeout = (log_status_interval - 1)
                    if self.player_steamid in self.bot.players.players_dict and self.bot.players.players_dict[self.player_steamid].is_responsive:
                        status = "active"
                    else:
                        status = "suspended"

                    log_message = "thread is {}, player is in region {} (I scan every {} seconds and log this every {} seconds)".format(
                        status, self.bot.players.players_dict[self.player_steamid].region, str(self.run_observers_interval), str(log_status_interval))
                    logger.debug(log_message)

        logger.debug("thread has stopped")

    def trigger_action(self, telnet_line):
        current_telnet_line = telnet_line  # make a copy, in case the current line gets changed during execution, no idea if that makes sense even
        logger.info(telnet_line)
        # print telnet_line

        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], current_telnet_line)
            if m:
                """
                this is a tricky bit! you need to define all variables used in any action here
                your IDE will tell you they are not used while in fact they are.
                the eval down there does the magic ^^ this is actually just to simplify things, you could access those
                with self.bot.whatever from within the functions and remove the parameters altogether
                so take some time to understand this. or just make it better if you know how ^^
                """

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
