from command_line_args import args_dict
from telnet_connection import TelnetConnection

from threading import Thread, Event
from logger import logger
import re
from datetime import datetime

from actions_authentication import actions_authentication
from actions_home import actions_home
from actions_lobby import actions_lobby, observers_lobby


class PlayerObserver(Thread):
    tn = None
    bot = None

    player_object = None
    logger = None

    player_is_alive = True

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
        last_telnet_line = bot.telnet_line

        log_status_interval = 10  # print player status ever ten seconds or so
        log_status_start = datetime.now()
        log_status_timeout = 0  # should log first, then timeout ^^
        """ this will run until the active_player_thread gets nuked from the bots main loop or shutdown method """
        while not self.stopped.wait(next_cycle):
            if (datetime.now() - log_status_start).total_seconds() > log_status_timeout:
                log_status_start = datetime.now()
                log_status_timeout = log_status_interval
                logger.debug("thread is active, player is in region " + player.region + " (I log this every " + str(log_status_interval) + " seconds)")

            """
            we need to hack a bit because of a nasty game bug
            if a player gets teleported while dead, he will get a black screen and has to relog
            upon respawn he will immediately die again. this can lead to a nasty death-loop
            so I switch the player off in the main loop after death and switch him back on after respawn ^^
            this is my third attempt at getting to a logic that actually workd. promising so far!
            """
            if self.observers is not None and self.player_is_alive:
                """
                these monitor stuff regardless of telnet activity!
                """
                for observer in self.observers:
                    player = self.player_object
                    locations = bot.locations_dict
                    function_name = observer[1]
                    function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                    function_name(*function_parameters)

            next_cycle = 1

        logger.debug("thread has stopped")

    def trigger_chat_action(self, telnet_line):
        """
        since we monitor the global telnet response, which runs at it's own speed, we have to make sure
        that we only react to new telnet_lines.
        so we check if there IS a line and then see if it differs from the last readout
        """
        bot = self.bot
        player = self.player_object

        current_telnet_line = telnet_line  # make a copy, in case the current line gets changed during execution
        logger.debug(current_telnet_line)
        logger.debug("possible action for " + player.name + " required")

        m = re.search(bot.match_types["chat_commands"], current_telnet_line)
        if m:
            """
            this is a tricky bit! you need to define all variables used in any action here
            your IDE will tell you they are not used while in fact they are.
            the eval down there does the magic ^^
            so take some time to understand this. or just make it better if you know how ^^
            """
            player_name = m.group('player_name')
            player = self.player_object
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
