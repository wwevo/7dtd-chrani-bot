from command_line_args import args_dict
from telnet_connection import TelnetConnection

from threading import Thread, Event
from logger import logger
import time
import re

from actions_authentication import actions_authentication
from actions_dev import actions_dev
from actions_home import actions_home
from actions_lobby import actions_lobby, observers_lobby
from actions_locations import actions_locations, observers_locations
from actions_whitelist import actions_whitelist, observers_whitelist


class PlayerObserver(Thread):
    tn = object
    bot = object

    run_observers_interval = int  # loop this every run_observers_interval seconds

    player_steamid = str
    logger = object

    player_actions = actions_whitelist + actions_authentication + actions_locations + actions_home + actions_lobby + actions_dev
    observers = observers_whitelist + observers_lobby + observers_locations

    def __init__(self, bot, event, player_steamid):
        """ using a telnet connection for every thread. shouldn't be that bad on a 24 player server """
        self.run_observers_interval = 1
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.bot = bot
        self.stopped = event
        self.player_steamid = str(player_steamid)

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

            if self.observers and player.is_alive():
                """ execute real-time observers
                these are run regardless of telnet activity!
                """
                command_queue = []
                for observer in self.observers:
                        players = self.bot.players
                        locations = self.bot.locations
                        function_name = observer[1]
                        function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                        command_queue.append([function_name, function_parameters])
                for command in command_queue:
                    if self.bot.players.players_dict[str(self.player_steamid)].is_alive():
                        command[0](*command[1])
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
        logger.debug(telnet_line)
        # print telnet_line

        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], current_telnet_line)
            if m:
                """
                this is a tricky bit! you need to define all variables used in any action here
                your IDE will tell you they are not used while in fact they are.
                the eval down there does the magic ^^
                so take some time to understand this. or just make it better if you know how ^^
                """
                players = self.bot.players
                locations = self.bot.locations

                player_name = m.group('player_name')
                for player_steamid, player_object in players.players_dict.iteritems():
                    if player_object.name == player_name:
                        player_object = players.players_dict[player_steamid]
                        break
                if player_object.name == player_name:
                    command = m.group('command')
                    # temp_command = None
                    if self.player_actions is not None:
                        for action in self.player_actions:
                            if player_object.is_responsive:
                                if (action[0] == "isequal" and action[1] == command) or (action[0] == "startswith" and command.startswith(action[1])):
                                    function_name = action[2]
                                    function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                    function_name(*function_parameters)
                            else:
                                break
