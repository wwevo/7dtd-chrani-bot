import re
from time import time
from threading import *

from bot.modules.logger import logger
from bot.modules.telnet_connection import TelnetConnection


class PlayerObserver(Thread):
    tn = object
    bot = object
    run_observers_interval = int  # loop this every run_observers_interval seconds

    player_steamid = str

    def __init__(self, event, bot, player_steamid):
        self.player_steamid = str(player_steamid)
        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(bot, bot.settings.get_setting_by_name('telnet_ip'), bot.settings.get_setting_by_name('telnet_port'), bot.settings.get_setting_by_name('telnet_password'))
        self.bot = bot
        self.run_observers_interval = 1

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        player_object = self.bot.players.get(self.player_steamid)
        self.trigger_action(player_object, "joined the game")

        if player_object.initialized is True:
            self.tn.send_message_to_player(player_object, "{} is ready and listening (v{})".format(self.bot.bot_name, self.bot.bot_version), color=self.bot.chat_colors['info'])

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time()

            if self.bot.observers_list:
                """ execute real-time observers
                these are run regardless of telnet activity!
                Everything that meeds to be checked periodically should be done in observers
                """
                command_queue = []
                for observer in self.bot.observers_list:
                    if observer["type"] == 'monitor':  # we only want the monitors here, the player is active, no triggers needed
                        observer_function_name = observer["action"]
                        observer_parameters = eval(observer["env"])  # yes. Eval. It's my own data, chill out!
                        command_queue.append({
                            "action": observer_function_name,
                            "command_parameters": observer_parameters
                        })

                for command in command_queue:
                    if player_object.is_responsive():
                        try:
                            command["action"](*command["command_parameters"])
                        except TypeError:
                            command["action"](command["command_parameters"])
                    else:
                        break

            if player_object.old_rot_x != player_object.rot_x:
                player_object.old_rot_x = player_object.rot_x
            if player_object.old_rot_y != player_object.rot_y:
                player_object.old_rot_y = player_object.rot_y
            if player_object.old_rot_z != player_object.rot_z:
                player_object.old_rot_z = player_object.rot_z

            execution_time = time() - profile_start
            next_cycle = self.run_observers_interval - execution_time
            # logger.debug("{} has {} of {} seconds left for calculations!".format(player_object.name, self.run_observers_interval - execution_time, self.run_observers_interval))

        logger.debug("thread has stopped")

    """
    loop through all available actions if they are a match for the given command and create a queue of actions to be fired
    loop though the command queue
    """
    def trigger_action(self, player_object, command_parameters):
        command_queue = []
        if self.bot.actions_list is not None:
            denied = False
            for player_action in self.bot.actions_list:
                function_category = player_action["group"]
                function_name = getattr(player_action["action"], 'func_name')
                if (player_action["match_mode"] == "isequal" and player_action["command"]["trigger"] == command_parameters) or (player_action["match_mode"] == "startswith" and command_parameters.startswith(player_action["command"]["trigger"])):
                    has_permission = self.bot.permissions.player_has_permission(player_object, function_name, function_category)
                    if (isinstance(has_permission, bool) and has_permission is True) or (player_action["essential"] is True):
                        function_object = player_action["action"]
                        command_queue.append({
                            "action": function_object,
                            "func_name": function_name,
                            "group": function_category,
                            "command_parameters": command_parameters
                        })
                    else:
                        denied = True
                        logger.info("Player {} denied trying to execute {}:{}".format(player_object.name, function_category, function_name))

            if len(command_queue) == 0:
                logger.debug("Player {} tried the command '/{}' for which I have no handler.".format(player_object.name, command_parameters))

            if denied is True:
                self.tn.send_message_to_player(player_object, "Access to this command is denied!", color=self.bot.chat_colors['warning'])

            for command in command_queue:
                try:
                    command["action"](self)
                except TypeError:
                    try:
                        command["action"](self, command["command_parameters"])
                        logger.info("Player {} has executed {}:{} with '/{}'".format(player_object.name, command["group"], command["func_name"], command["command_parameters"]))
                    except Exception as e:
                        logger.debug("Player {} tried to execute {}:{} with '/{}', which lead to: {}".format(player_object.name, command["group"], command["func_name"], command["command_parameters"], e))

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
