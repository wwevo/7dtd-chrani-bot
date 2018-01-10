from command_line_args import args_dict
from telnet_connection import TelnetConnection

from threading import Thread, Event
from logger import logger
import time
import re

from actions_authentication import actions_authentication
from actions_home import actions_home
from actions_lobby import actions_lobby, observers_lobby


class PlayerObserver(Thread):
    tn = None
    bot = None

    run_observers_interval = 1  # loop this every run_observers_interval seconds

    player_object = None
    logger = None

    player_actions = actions_authentication + actions_home + actions_lobby
    observers = observers_lobby

    def __init__(self, bot, event, player):
        """ using a telnet connection for every thread. shouldn't be that bad on a 24 player server """
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])

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
        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()
            if time.time() - log_status_start > log_status_timeout:
                """ prepare log-output
                
                we don't have it clogged with endless meaningless lines
                """
                log_status_start = time.time()
                log_status_timeout = (log_status_interval - 1)
                if player.is_responsive:
                    status = "active"
                else:
                    status = "suspended"
                logger.debug("thread is " + status + ", player is in region " + player.region + " (I scan every " + str(self.run_observers_interval) + " seconds and log this every " + str(log_status_interval) + " seconds)")

            """ monitor player movement
            
            make sure a moving player is accepted as responsive, in case the bot got started when players where already
            in the game, making us unable to read the telnet-logs regarding player-spawn
            this is just a fail-safe and has a considerable delay/lag and is depending on the listplayers poll interval
            in the main loop! we still have to use the games telnet responses in the main loop to react 'directly'
            this is ONLY for detecting players already online before the bot got started!!
            
            a wish for a17? enhance the listplayer command and include death-state (alive, bedroll-screen, dead) """
            if player.is_responsive and player.is_dead():
                player.switch_off("observer")

            if not player.is_responsive and player.check_if_lifesigns_have_changed():
                player.switch_on("observer")

            if self.observers and player.is_responsive:
                """ execute real-time observers

                if a player gets teleported while dead, he will get a black screen and has to relog
                upon respawn he will immediately die again. this can lead to a nasty death-loop
                so I switch the player off in the main loop after death and switch him back on after respawn ^^
                this is my third attempt at getting to a logic that actually works. promising so far!

                these are run regardless of telnet activity!
                """
                for observer in self.observers:
                    player = self.player_object
                    locations = bot.locations_dict
                    function_name = observer[1]
                    function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                    function_name(*function_parameters)

            profile_end = time.time()
            execution_time = profile_end - profile_start
            next_cycle = self.run_observers_interval - execution_time

        logger.debug("thread has stopped")

    def trigger_action(self, telnet_line):
        bot = self.bot
        player = self.player_object

        current_telnet_line = telnet_line  # make a copy, in case the current line gets changed during execution, no idea if that makes sense even
        logger.debug(telnet_line)
        logger.debug("possible action for " + player.name + " required")

        for match_type in bot.match_types:
            m = re.search(bot.match_types[match_type], current_telnet_line)
            if m:
                """
                this is a tricky bit! you need to define all variables used in any action here
                your IDE will tell you they are not used while in fact they are.
                the eval down there does the magic ^^
                so take some time to understand this. or just make it better if you know how ^^
                """
                player_name = m.group('player_name')
                locations = bot.locations_dict

                if player.name == player_name:
                    command = m.group('command')
                    temp_command = None
                    if self.player_actions is not None:
                        for action in self.player_actions:
                            if action[0] == "isequal":
                                temp_command = command
                            if action[0] == "startswith":
                                temp_command = command.split(' ', 1)[0]

                            if action[1] == temp_command:
                                function_name = action[2]
                                function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                function_name(*function_parameters)
