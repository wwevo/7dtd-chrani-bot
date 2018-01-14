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
from actions_dev import actions_dev


class PlayerObserver(Thread):
    tn = None
    bot = None

    run_observers_interval = 1  # loop this every run_observers_interval seconds

    player_object = None
    logger = None

    player_actions = actions_dev + actions_authentication + actions_home + actions_lobby
    observers = observers_lobby + observers_home

    def __init__(self, bot, event, player):
        """ using a telnet connection for every thread. shouldn't be that bad on a 24 player server """
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.tn.bot = bot
        self.bot = bot

        self.stopped = event
        self.player_object = player

        Thread.__init__(self)

    def run(self):
        """ some simplifications so we don't need to use .self all the time """
        bot = self.bot
        player = self.player_object

        next_cycle = 0

        log_status_interval = 5  # print player status ever ten seconds or so
        log_status_start = 0
        log_status_timeout = 0  # should log first, then timeout ^^
        player.store_player_lifesigns()  # save the starting-values of our player's vitals / position

        self.tn.send_message_to_player(player, "bot " + bot.name + " is ready and listening")

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            if self.observers and player.is_responsive:
                """ execute real-time observers

                if a player gets teleported while dead, he will get a black screen and has to relog
                upon respawn he will immediately die again. this can lead to a nasty death-loop
                so I switch the player off in the main loop after death and switch him back on after respawn ^^
                this is my third attempt at getting to a logic that actually works. promising so far!

                these are run regardless of telnet activity!
                """
                command_queue = []
                for observer in self.observers:
                        player_object = self.player_object
                        locations = bot.locations_dict
                        function_name = observer[1]
                        function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                        command_queue.append([function_name, function_parameters])
                for command in command_queue:
                    if player.is_alive():
                        command[0](*command[1])
                    else:
                        break

            execution_time = time.time() - profile_start
            next_cycle = self.run_observers_interval - execution_time

            if time.time() - log_status_start > log_status_timeout:
                """ prepare log-output

                we don't have it clogged with endless meaningless lines
                """
                log_message = "executed player_observer loop. that took me like totally less than {} seconds!!".format(
                    execution_time)
                logger.debug(log_message)

                log_status_start = time.time()
                log_status_timeout = (log_status_interval - 1)
                if player.is_responsive:
                    status = "active"
                else:
                    status = "suspended"

                log_message = "thread is {}, player is in region {} (I scan every {} seconds and log this every {} seconds)".format(
                    status, player.region, str(self.run_observers_interval), str(log_status_interval))
                logger.debug(log_message)

        logger.debug("thread has stopped")

    def trigger_action(self, telnet_line):
        bot = self.bot

        current_telnet_line = telnet_line  # make a copy, in case the current line gets changed during execution, no idea if that makes sense even
        logger.debug(telnet_line)

        for match_type in bot.match_types:
            m = re.search(bot.match_types[match_type], current_telnet_line)
            if m:
                """
                this is a tricky bit! you need to define all variables used in any action here
                your IDE will tell you they are not used while in fact they are.
                the eval down there does the magic ^^
                so take some time to understand this. or just make it better if you know how ^^
                """
                players = bot.players_dict
                locations = bot.locations_dict

                player_name = m.group('player_name')
                for player_steamid, player_object in players.iteritems():
                    if player_object.name == player_name:
                        player_object = players[player_steamid]
                        break
                if player_object.name == player_name:
                    command = m.group('command')
                    # temp_command = None
                    if self.player_actions is not None:
                        for action in self.player_actions:
                            # if action[0] == "isequal":
                            #     temp_command = command
                            # if action[0] == "startswith":
                            #     temp_command = command.split(' ', 1)[0]

                            if player_object.is_responsive:
                                if action[1] == command or command.startswith(action[1]):
                                # if action[1] == temp_command:
                                    function_name = action[2]
                                    function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                    function_name(*function_parameters)
                            else:
                                break
