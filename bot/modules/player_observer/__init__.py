import re
import time
from threading import *
from collections import deque

import actions

from player_thread import PlayerThread
from bot.modules.logger import logger

from bot.objects.player import Player

class PlayerObserver(Thread):
    chrani_bot = object
    actions = object

    stopped = object

    run_observer_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float
    active_player_threads_dict = dict  # contains link to the players observer-thread

    action_queue = deque

    def __init__(self, event, chrani_bot):
        self.chrani_bot = chrani_bot

        self.action_queue = deque()
        self.active_player_threads_dict = {}

        self.run_observer_interval = 1.0
        self.last_execution_time = 0.0

        self.actions = actions
        self.actions_list = actions.actions_list

        self.stopped = event
        Thread.__init__(self)

    def start_player_thread(self, player_object):
        player_thread_stop_flag = Event()
        player_thread = PlayerThread(player_thread_stop_flag, self.chrani_bot, player_object.steamid)  # I'm passing the bot into it to have easy access to it's variables
        player_thread.name = player_object.steamid  # nice to have for the logs
        player_thread.isDaemon()
        player_thread.start()
        self.chrani_bot.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
        self.chrani_bot.socketio.emit('update_leaflet_markers', self.chrani_bot.players.get_leaflet_marker_json([player_object]), namespace='/chrani-bot/public')
        self.active_player_threads_dict.update({player_object.steamid: {"event": player_thread_stop_flag, "thread": player_thread}})
        return player_thread

    def stop_player_thread(self, player_object):
        self.chrani_bot.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
        self.chrani_bot.socketio.emit('update_leaflet_markers', self.chrani_bot.players.get_leaflet_marker_json([player_object]), namespace='/chrani-bot/public')
        pass

    def manage_online_players(self):
        # get all currently online players and store them in a dictionary
        listplayers_dict = self.chrani_bot.telnet_observer.actions.common.get_active_action_result("system", "lp")
        if len(listplayers_dict) <= 0:
            return listplayers_dict

        # prune players not online anymore
        for player in set(self.chrani_bot.players.players_dict) - set(listplayers_dict.keys()):
            self.chrani_bot.players.players_dict[player].is_online = False

        # create new player entries / update existing ones
        for player_steamid, player_dict in listplayers_dict.iteritems():
            try:
                player_object = self.chrani_bot.players.get_by_steamid(player_steamid)
                # player is already online and needs updating
                player_object.update(**player_dict)
                self.chrani_bot.players.upsert(player_object)
            except KeyError:  # player is completely new
                player_object = Player(**player_dict)
                self.chrani_bot.players.upsert(player_object, save=True)
            # there should be a valid object state here now ^^

        """ handle player-threads """
        for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
            """ start player_observer_thread for each player not already being observed """
            if player_object.steamid not in self.chrani_bot.player_observer.active_player_threads_dict and player_object.is_online:
                player_thread = self.chrani_bot.player_observer.start_player_thread(player_object)
                player_thread.trigger_action(player_object, "found in the world")

        players_to_obliterate = []
        for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
            if player_steamid in self.chrani_bot.player_observer.active_player_threads_dict and not player_object.is_online:
                """ prune all active_player_threads from players no longer online """
                self.chrani_bot.player_observer.stop_player_thread(player_object)
                active_player_thread = self.chrani_bot.player_observer.active_player_threads_dict[player_steamid]
                stop_flag = active_player_thread["thread"]
                stop_flag.stopped.set()
                self.chrani_bot.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                self.chrani_bot.socketio.emit('update_leaflet_markers', self.chrani_bot.players.get_leaflet_marker_json([player_object]), namespace='/chrani-bot/public')

                del self.chrani_bot.player_observer.active_player_threads_dict[player_steamid]
            if player_object.is_to_be_obliterated is True:
                player_object.is_online = False
                players_to_obliterate.append(player_object)

        for player_object in players_to_obliterate:
            self.chrani_bot.socketio.emit('remove_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
            self.chrani_bot.socketio.emit('remove_leaflet_markers', self.chrani_bot.players.get_leaflet_marker_json([player_object]), namespace='/chrani-bot/public')
            self.chrani_bot.players.remove(player_object)

        player_threads_to_remove = []
        for player_steamid, player_thread in self.chrani_bot.player_observer.active_player_threads_dict.iteritems():
            if player_steamid not in self.chrani_bot.players.players_dict:
                player_threads_to_remove.append(player_steamid)

        for player_steamid in player_threads_to_remove:
            del self.chrani_bot.player_observer.active_player_threads_dict[player_steamid]

        return listplayers_dict

    """ scans a given telnet-line for the players name and any possible commmand as defined in the match-types list, then fires that action """
    def trigger_action_by_telnet(self, telnet_line):
        for match_type in self.chrani_bot.match_types:
            m = re.search(self.chrani_bot.match_types[match_type], telnet_line)
            if m:
                player_name = None
                player_name_found = False
                try:
                    player_name = m.group('player_name')
                    player_name_found = True
                except IndexError:
                    try:
                        player_entity_id = m.group('entity_id')
                        player_steamid = self.chrani_bot.players.entityid_to_steamid(player_entity_id)
                        player_object = self.chrani_bot.players.get_by_steamid(player_steamid)
                        player_name = player_object.name
                        player_name_found = True
                    except IndexError:
                        pass

                if player_name_found:
                    command = m.group('command')
                    for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
                        if player_object.name == player_name:
                            self.chrani_bot.player_observer.actions.common.trigger_action(self.chrani_bot, player_object, player_object, command)
                            break

    def get_a_bunch_of_actions(self, this_many_actions):
        player_actions = []
        current_queue_length = 0
        done = False
        while (current_queue_length < this_many_actions) and not done:
            try:
                player_actions.append(self.action_queue.popleft())
                current_queue_length += 1
            except IndexError:
                done = True

        if len(player_actions) >= 1:
            return player_actions
        else:
            return False

    def execute_queue(self, count):
        actions = self.get_a_bunch_of_actions(count)
        if not actions:
            return True

        for action in actions:
            try:
                self.actions.common.trigger_action(self.chrani_bot, action["source_player"], action["target_player"], action["command"])
            except Exception as e:
                logger.error("{error} {type}".format(error=e, type=type(e)))
                pass

        return len(actions)

    def run(self):
        logger.info("player observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            """ so far there is nothing to do here, just signalling readiness to our custodian """
            self.chrani_bot.custodian.check_in('player_observer', True)

            if self.chrani_bot.is_paused is not False:
                time.sleep(1)
                continue

            profile_start = time.time()
            self.manage_online_players()
            
            self.last_execution_time = time.time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("player observer thread has stopped")
