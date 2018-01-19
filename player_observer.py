from command_line_args import args_dict
from telnet_connection import TelnetConnection

from threading import Thread, Event
from logger import logger
import time
import re
import pprint

from actions_authentication import actions_authentication
from actions_home import actions_home, observers_home
from actions_lobby import actions_lobby, observers_lobby
from actions_whitelist import actions_whitelist, observers_whitelist


class PlayerObserver(Thread):
    tn = None
    bot = None

    run_observers_interval = 1  # loop this every run_observers_interval seconds

    player_steamid = None
    logger = None

    player_actions = actions_whitelist + actions_authentication + actions_home + actions_lobby
    observers = observers_whitelist + observers_lobby + observers_home

    def __init__(self, bot, event, player_steamid):
        """ using a telnet connection for every thread. shouldn't be that bad on a 24 player server """
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.tn.bot = bot
        self.bot = bot

        self.stopped = event
        self.player_steamid = str(player_steamid)

        Thread.__init__(self)

    def run(self):
        next_cycle = 0

        log_status_interval = 5  # print player status ever ten seconds or so
        log_status_start = 0
        log_status_timeout = 0  # should log first, then timeout ^^
        self.bot.players.players_dict[self.player_steamid].store_player_lifesigns()  # save the starting-values of our player's vitals / position
        self.tn.send_message_to_player(self.bot.players.players_dict[self.player_steamid], "bot " + self.bot.name + " is ready and listening")
        self.bot.players.load(self.player_steamid)

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            player = self.bot.players.get(self.player_steamid)
            if self.observers and player is not False and player.is_responsive:
                """ execute real-time observers

                if a player gets teleported while dead, he will get a black screen and has to relog
                upon respawn he will immediately die again. this can lead to a nasty death-loop
                so I switch the player off in the main loop after death and switch him back on after respawn ^^
                this is my third attempt at getting to a logic that actually works. promising so far!

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

            # if not player.is_responsive and player.check_if_lifesigns_have_changed():
            #     player.switch_on("observer")

            execution_time = time.time() - profile_start
            next_cycle = self.run_observers_interval - execution_time

            if time.time() - log_status_start > log_status_timeout:
                """ prepare log-output

                so we don't have it clogged with endless meaningless lines
                """
                log_message = "executed player_observer loop. that took me like totally less than {} seconds!!".format(
                    execution_time)
                logger.debug(log_message)

                log_status_start = time.time()
                log_status_timeout = (log_status_interval - 1)
                if self.bot.players.players_dict[self.player_steamid].is_responsive:
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
