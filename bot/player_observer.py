import re
from time import time
from threading import *

from bot.logger import logger
from bot.telnet_connection import TelnetConnection


class PlayerObserver(Thread):
    tn = object
    bot = object
    run_observers_interval = int  # loop this every run_observers_interval seconds

    player_steamid = str

    def __init__(self, event, bot, player_steamid):
        self.player_steamid = str(player_steamid)
        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(bot, bot.settings_dict['telnet_ip'], bot.settings_dict['telnet_port'], bot.settings_dict['telnet_password'])
        self.bot = bot
        self.run_observers_interval = 1

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        player_object = self.bot.players.get(self.player_steamid)
        self.trigger_action(player_object, "joined the game")

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time()

            if player_object.has_health():
                player_object.switch_on()
            else:
                player_object.switch_off()

            if player_object.is_responsive:
                if self.bot.observers:
                    """ execute real-time observers
                    these are run regardless of telnet activity!
                    """
                    command_queue = []
                    for observer in self.bot.observers:
                        if observer[0] == 'monitor':  # we only want the monitors here, the player is active, no triggers needed
                            observer_function_name = observer[2]
                            observer_parameters = eval(observer[3])  # yes. Eval. It's my own data, chill out!
                            command_queue.append([observer_function_name, observer_parameters])
                    for command in command_queue:
                        if player_object.is_responsive:
                            try:
                                command[0](*command[1])
                            except TypeError:
                                command[0](command[1])
                        else:
                            break

            execution_time = time() - profile_start
            next_cycle = self.run_observers_interval - execution_time
        logger.debug("thread has stopped")

    """
    loop through all available actions if they are a match for the given command and create a queue of actions to be fired
    loop though the command queue
    """
    def trigger_action(self, player_object, command):
        command_queue = []
        if self.bot.player_actions is not None:
            for player_action in self.bot.player_actions:
                function_category = player_action["group"]
                function_name = getattr(player_action["action"], 'func_name')
                if (player_action["match_mode"] == "isequal" and player_action["command"]["trigger"] == command) or (player_action["match_mode"] == "startswith" and command.startswith(player_action["command"]["trigger"])):
                    function_object = player_action["action"]
                    # chat_command = player_action["command"]
                    command_queue.append([function_object, function_name, function_category, command, player_action["essential"]])

            if len(command_queue) == 0:
                logger.info("Player {} tried the command '{}' for which I have no handler.".format(player_object.name, command))
                return False

            for command in command_queue:
                has_permission = self.bot.permissions.player_has_permission(player_object, command[1], command[2])
                if (isinstance(has_permission, bool) and has_permission is True) or (command[4] is True):
                    try:
                        command[0](self)
                    except TypeError:
                        try:
                            command[0](self, command[3])
                        except Exception as e:
                            logger.debug("Player {} tried to execute {}:{} with '/{}', which lead to: {}".format(player_object.name, command[2], command[1], command[3], e))
                            pass

                    logger.info("Player {} has executed {}:{} with '/{}'".format(player_object.name, command[2], command[1], command[3]))
                else:
                    self.bot.tn.send_message_to_player(player_object, "Access denied, you need to be {}".format(has_permission))
                    logger.info("Player {} denied trying to execute {}:{}".format(player_object.name, command[2], command[1]))

    """ scans a given telnet-line for the players name and any possible commmand as defined in the match-types list, then fires that action """
    def trigger_action_by_telnet(self, telnet_line):
        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], telnet_line)
            if m:
                player_name = m.group('player_name')
                command = m.group('command')
                for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                    if player_object.name == player_name:
                        self.trigger_action(player_object, command)
                        break
