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

    def __init__(self, event, bot, player_steamid):
        self.player_steamid = str(player_steamid)
        self.player_object = bot.players.get_by_steamid(self.player_steamid)

        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(bot, bot.settings.get_setting_by_name('telnet_ip'), bot.settings.get_setting_by_name('telnet_port'), bot.settings.get_setting_by_name('telnet_password'))
        self.bot = bot
        self.run_observers_interval = 1

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        player_object = self.player_object
        bot.actions.common.trigger_action(self.bot, None, player_object, "joined the game")

        if player_object.initialized is True:
            self.tn.send_message_to_player(player_object, "{} is ready and listening (v{})".format(self.bot.bot_name, self.bot.bot_version), color=self.bot.chat_colors['info'])

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            if self.bot.is_paused is True:
                sleep(1)
                continue

            profile_start = time()

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
                    if player_object.is_responsive():
                        try:
                            command["action"](command["command_parameters"])
                        except TypeError:
                            command["action"](*command["command_parameters"])
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
            # logger.debug("{} needed {} seconds to execute all scripts!".format(player_object.name, execution_time))

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
