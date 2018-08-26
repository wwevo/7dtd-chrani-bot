import re
from time import time, sleep
from threading import *

import bot.actions
from bot.modules.logger import logger
from bot.modules.telnet_connection import TelnetConnection


class PlayerObserver(Thread):
    tn = object
    bot = object

    player_steamid = str
    player_object = object

    run_observers_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float

    def __init__(self, event, bot, player_steamid):
        self.player_steamid = str(player_steamid)

        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(bot, bot.settings.get_setting_by_name('telnet_ip'), bot.settings.get_setting_by_name('telnet_port'), bot.settings.get_setting_by_name('telnet_password'))
        self.bot = bot
        self.run_observers_interval = 1
        self.last_execution_time = 0.0

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            self.player_object = self.bot.players.get_by_steamid(self.player_steamid)
            if self.bot.is_paused is not False:
                sleep(1)
                continue

            profile_start = time()
            if self.player_object.is_responsive() is False:
                player_moved_mouse = False
                if self.player_object.old_rot_x != self.player_object.rot_x:
                    player_moved_mouse = True
                if self.player_object.old_rot_z != self.player_object.rot_z:
                    player_moved_mouse = True

                if player_moved_mouse is True:
                    self.player_object.initialized = True
                    logger.debug("{} has been caught moving their head :)".format(self.player_object.name))

                if self.player_object.old_rot_x != self.player_object.rot_x:
                    self.player_object.old_rot_x = self.player_object.rot_x
                if self.player_object.old_rot_y != self.player_object.rot_y:
                    self.player_object.old_rot_y = self.player_object.rot_y
                if self.player_object.old_rot_z != self.player_object.rot_z:
                    self.player_object.old_rot_z = self.player_object.rot_z

            if self.bot.observers_list:
                """ execute real-time observers
                these are run regardless of telnet activity!
                Everything that needs to be checked periodically should be done in observers
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
                    if self.player_object.is_responsive():
                        try:
                            result = command["action"](command["command_parameters"])
                            if not result:
                                continue
                        except TypeError:
                            command["action"](*command["command_parameters"])
                    else:
                        break

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observers_interval - self.last_execution_time

        logger.debug("thread has stopped")

    def trigger_action(self, target_player, command):
        bot.actions.common.trigger_action(self.bot, self.player_object, target_player, command)

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
