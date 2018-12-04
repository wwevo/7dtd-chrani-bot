import re
from time import time, sleep
import math
from threading import *
from collections import deque

import bot.modules.actions
from bot.modules.logger import logger
from bot.assorted_functions import TimeoutError


class PlayerObserver(Thread):
    bot = object

    player_steamid = str
    player_object = object

    run_observers_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float
    action_queue = deque

    def __init__(self, event, chrani_bot, player_steamid):
        self.player_steamid = str(player_steamid)

        logger.info("thread started for player " + self.player_steamid)

        self.bot = chrani_bot
        self.run_observers_interval = 1
        self.last_execution_time = 0.0

        self.action_queue = deque()

        self.stopped = event
        Thread.__init__(self)

    def player_moved_mouse(self):
        player_moved_mouse = False
        if self.player_object.old_rot_x == 0.0 and self.player_object.old_rot_y == 0.0 and self.player_object.old_rot_z == 0.0:
            self.player_object.old_rot_x = self.player_object.rot_x
            self.player_object.old_rot_y = self.player_object.rot_y
            self.player_object.old_rot_z = self.player_object.rot_z

        if self.player_object.old_rot_x != self.player_object.rot_x:
            player_moved_mouse = True
        if self.player_object.old_rot_z != self.player_object.rot_z:
            player_moved_mouse = True

        if self.player_object.old_rot_x != self.player_object.rot_x:
            self.player_object.old_rot_x = self.player_object.rot_x
        if self.player_object.old_rot_y != self.player_object.rot_y:
            self.player_object.old_rot_y = self.player_object.rot_y
        if self.player_object.old_rot_z != self.player_object.rot_z:
            self.player_object.old_rot_z = self.player_object.rot_z
            
        return player_moved_mouse

    def player_moved(self):
        player_moved = False

        if not isinstance(self.player_object.pos_x, float) or not isinstance(self.player_object.pos_y, float) or not isinstance(self.player_object.pos_z, float):
            return player_moved
        # at this point, pos_x+y+z has a value, so we can store the old one as well. if either hadn't got a value, the player certainly wouldn't be initialized completely.

        # if old_pos_x+y+z is not set, we need to set it, or the player_moved_bias will fire later on
        if not isinstance(self.player_object.old_pos_x, float):
            self.player_object.old_pos_x = self.player_object.pos_x
        if not isinstance(self.player_object.old_pos_y, float):
            self.player_object.old_pos_y = self.player_object.pos_y
        if not isinstance(self.player_object.old_pos_z, float):
            self.player_object.old_pos_z = self.player_object.pos_z

        # using >= 2 to catch eventualities where players are spawning slightly into the ground or a wall, being moved around by the game because of it
        player_moved_bias = [
            math.fabs(self.player_object.old_pos_x - self.player_object.pos_x) >= 2,
            math.fabs(self.player_object.old_pos_y - self.player_object.pos_y) >= 2,
            math.fabs(self.player_object.old_pos_z - self.player_object.pos_z) >= 2
        ]

        if any(player_moved_bias):
            self.player_object.old_pos_x = self.player_object.pos_x
            self.player_object.old_pos_y = self.player_object.pos_y
            self.player_object.old_pos_z = self.player_object.pos_z
            player_moved = True

        return player_moved

    def run(self):
        self.player_object = self.bot.players.get_by_steamid(self.player_steamid)
        self.player_object.is_online = True
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            if not self.bot.has_connection:
                raise IOError

            if self.bot.is_paused is not False:
                sleep(1)
                continue

            profile_start = time()

            player_is_responsive = self.player_object.is_responsive()
            player_moved = self.player_moved()
            if player_is_responsive and player_moved:
                if not self.player_object.initialized:
                    self.player_object.initialized = True
                json = self.bot.players.get_leaflet_marker_json([self.player_object])
                self.bot.socketio.emit('update_leaflet_markers', json, namespace='/chrani-bot/public')

            done = False
            while not done:
                try:
                    action = self.action_queue.popleft()
                    bot.modules.actions.common.trigger_action(self.bot, self.player_object, action["target_player"], action["command"])
                except IndexError:
                    done = True

            if self.bot.observers_dict:
                """ execute real-time observers
                these are run regardless of telnet activity!
                Everything directly player-related that needs to be checked periodically should be done in observers
                """
                command_queue = []
                for name, observer in self.bot.observers_dict.iteritems():
                    if observer["type"] == 'monitor':  # we only want the monitors here, the player is active, no triggers needed
                        observer_function_name = observer["action"]
                        command_queue.append({
                            "observer": observer_function_name,
                            "is_active": self.bot.observers_controller[name]["is_active"]
                        })

                for command in command_queue:
                    if command["is_active"]:
                        try:
                            result = command["observer"](self.bot, self)
                        except TypeError as error:
                            logger.debug("{} had a type error ({})".format(command["observer"], error.message))
                            pass
                        except AttributeError as error:
                            logger.debug("{} had an attribute error! ({})".format(command["observer"], error.message))
                            pass
                        except IOError as error:
                            logger.debug("{} had an input/output error! ({})".format(command["observer"], error.message))
                            self.bot.has_connection = False
                            pass
                        except TimeoutError as error:
                            logger.debug("{} had a timeout! ({})".format(command["observer"], error.message))
                            pass
                        except Exception as error:
                            logger.error("{} had an unknown error! ({})".format(command["observer"], type(error)))
                            pass

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observers_interval - self.last_execution_time

        logger.debug("thread has stopped")

    def trigger_action(self, target_player, command):
        self.action_queue.append({"target_player": target_player, "command": command})

    """ scans a given telnet-line for the players name and any possible commmand as defined in the match-types list, then fires that action """
    def trigger_action_by_telnet(self, telnet_line):
        for match_type in self.bot.match_types:
            m = re.search(self.bot.match_types[match_type], telnet_line)
            if m:
                player_name = None
                player_name_found = False
                try:
                    player_name = m.group('player_name')
                    player_name_found = True
                except IndexError:
                    pass

                try:
                    player_entity_id = m.group('entity_id')
                    player_steamid = self.bot.players.entityid_to_steamid(player_entity_id)
                    player_object = self.bot.players.get_by_steamid(player_steamid)
                    player_name = player_object.name
                    player_name_found = True
                except IndexError:
                    pass

                if player_name_found:
                    command = m.group('command')
                    for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                        if player_object.name == player_name:
                            self.trigger_action(player_object, command)
                            break
