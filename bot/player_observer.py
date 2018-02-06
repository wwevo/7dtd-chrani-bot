import re
import time
from threading import Thread

from bot.command_line_args import args_dict
from bot.logger import logger
from bot.telnet_connection import TelnetConnection


class PlayerObserver(Thread):
    tn = object
    bot = object
    logger = object
    run_observers_interval = int  # loop this every run_observers_interval seconds

    player_steamid = str

    def __init__(self, bot, event, player_steamid):
        self.player_steamid = str(player_steamid)
        logger.info("thread started for player " + self.player_steamid)

        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
        self.bot = bot
        self.run_observers_interval = 1

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        next_cycle = 0
        self.tn.send_message_to_player(self.bot.players.players_dict[self.player_steamid], "{} is ready and listening".format(self.bot.name), 'db8b0b')

        player_object = self.bot.players.get(self.player_steamid)

        # this will run until the active_player_thread gets nuked from the bots main loop or shutdown method
        while not self.stopped.wait(next_cycle):
            profile_start = time.time()

            if self.bot.observers:
                if player_object.is_responsive:
                    """ execute real-time observers
                    these are run regardless of telnet activity!
                    """
                    command_queue = []
                    for observer in self.bot.observers:
                        function_name = observer[1]
                        function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                        command_queue.append([function_name, function_parameters])
                    for command in command_queue:
                        if player_object.is_responsive:
                            try:
                                command[0](*command[1])
                            except TypeError:
                                command[0](command[1])
                        else:
                            break
                else:
                    if player_object.has_health():
                        player_object.switch_on("caught you alive and kicking")

                execution_time = time.time() - profile_start
                next_cycle = self.run_observers_interval - execution_time
        logger.debug("thread has stopped")

    def trigger_action(self, telnet_line):
        current_telnet_line = telnet_line

        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], current_telnet_line)
            if m:
                player_name = m.group('player_name')
                for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                    if player_object.name == player_name:
                        player_object = self.bot.players.players_dict[player_steamid]

                        command = m.group('command')
                        command_queue = []
                        if self.bot.player_actions is not None:
                            for player_action in self.bot.player_actions:
                                if player_object.is_responsive:  # TODO: integrate permission check here
                                    function_category = player_action[4]
                                    function_name = getattr(player_action[2], 'func_name')
                                    if (player_action[0] == "isequal" and player_action[1] == command) or (player_action[0] == "startswith" and command.startswith(player_action[1])):
                                        function_object = player_action[2]
                                        function_parameters = eval(player_action[3])  # yes. Eval. It's my own data, chill out!
                                        command_queue.append([function_object, function_parameters, function_name, function_category])
                                else:
                                    break
                            for command in command_queue:
                                has_permission = self.bot.permissions.player_has_permission(player_object, command[2], command[3])
                                if has_permission == None or isinstance(has_permission, bool) and has_permission is True:
                                    try:
                                        command[0](*command[1])
                                    except TypeError:
                                        command[0](command[1])

                                    logger.info("Player {} has executed {}".format(player_object.name, command[2]))
                                else:
                                    self.bot.tn.send_message_to_player(player_object, "Access denied, you need to be {}".format(has_permission))
                                    logger.info("Player {} denied trying to execute {}".format(player_object.name, command[2]))
                            if len(command_queue) == 0:
                                self.bot.tn.send_message_to_player(player_object, "The command '/{}' is unknown to me. Maybe a typo?".format(command))

                        break