import re
import time
from threading import *
from collections import deque

import actions

from player_thread import PlayerThread
from bot.modules.logger import logger

from bot.objects.player import Player


class PlayerObserver(Thread):
    stopped = object

    chrani_bot = object
    actions = object
    actions_list = list

    run_observer_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float

    action_queue = deque

    def __init__(self, chrani_bot):
        self.chrani_bot = chrani_bot

        self.stopped = Event()
        Thread.__init__(self)

    def setup(self):
        self.name = 'player observer'
        self.setDaemon(daemonic=True)

        self.action_queue = deque()
        self.chrani_bot.dom["bot_data"]["active_threads"]["player_observer"] = {}

        self.run_observer_interval = 1.0
        self.last_execution_time = 0.0

        self.actions = actions
        self.actions_list = actions.actions_list

        return self

    def start(self):
        logger.info("player observer thread started")
        Thread.start(self)
        return self

    def cleanup(self):
        try:
            for player_steamid in self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer"):
                """ kill them ALL! """
                active_player_thread = self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer").get(player_steamid)
                active_player_thread.stopped.set()

            self.chrani_bot.dom["bot_data"]["active_threads"]["player_observer"] = {}
        except AttributeError:
            pass

    def start_player_thread(self, player_object):
        if player_object.steamid in self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer"):
            # already being observed
            return self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer").get(player_object.steamid)

        player_thread = PlayerThread(self.chrani_bot, player_object.steamid).setup().start()  # I'm passing the bot into it to have easy access to it's variables
        player_thread.isDaemon()
        self.chrani_bot.dom["bot_data"]["active_threads"]["player_observer"][player_object.steamid] = player_thread
        return player_thread

    def stop_player_thread(self, player_object):
        active_player_thread = self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer").get(player_object.steamid)
        active_player_thread.stopped.set()
        del self.chrani_bot.dom["bot_data"]["active_threads"]["player_observer"][player_object.steamid]

        player_object.is_online = False
        player_object.is_logging_in = False
        player_object.update()

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
                            self.chrani_bot.players.upsert(player_object, save=True)
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
        next_cycle = 0
        while not self.stopped.wait(next_cycle) or not self.chrani_bot.telnet_observer.stopped.isSet():
            """ so far there is nothing to do here, just signalling readiness to our custodian """
            self.chrani_bot.custodian.check_in('player_observer', True)

            if self.chrani_bot.is_paused is not False:
                time.sleep(1)
                continue

            profile_start = time.time()
            # get all currently online players and store them in a dictionary
            listplayers_dict = self.chrani_bot.dom.get("bot_data").get("telnet_observer").get("system", {}).get(self.chrani_bot.settings.get_setting_by_name(name='listplayers_method'), {}).get("result", "")
            if len(listplayers_dict) <= 0:
                # no players are online, so we can set them all to offline here
                listplayers_dict = {}
                for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
                    self.chrani_bot.dom["bot_data"]["player_data"][player_steamid]["is_online"] = False
                    player_object.is_online = False
                    player_object.update()

            for player_steamid, player_dict in listplayers_dict.iteritems():
                # This only concerns players already in the games active list!
                try:  # player is already online and needs updating
                    player_object = self.chrani_bot.players.get_by_steamid(player_steamid)
                    player_object.update(**player_dict)
                    self.chrani_bot.socketio.emit('refresh_player_status', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                except KeyError:  # player is completely new and needs file creation
                    player_object = Player(**player_dict)
                    player_object.update(**self.chrani_bot.dom.get("bot_data").get("player_data").get(player_steamid, {}))
                    self.chrani_bot.players.upsert(player_object, save=True)

                if not player_dict["is_online"]:
                    player_dict["is_logging_in"] = True

                self.chrani_bot.dom["bot_data"]["player_data"][player_steamid].update(**player_dict)

            """ handle player-threads """
            for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
                """ start player_observer_thread for each player not already being observed """
                if player_object.steamid not in self.chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer") and player_steamid != "system":
                    # manually trigger actions for players found through lp response
                    if self.chrani_bot.dom["bot_data"]["player_data"][player_steamid]["is_logging_in"] is True:
                        player_thread = self.start_player_thread(player_object)
                        player_thread.trigger_action(player_object, "found in the stream")
                    if self.chrani_bot.dom["bot_data"]["player_data"][player_steamid]["is_online"] is True:
                        player_thread = self.start_player_thread(player_object)
                        player_thread.trigger_action(player_object, "found in the world")

            players_to_obliterate = []
            for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
                if self.chrani_bot.dom.get("bot_data").get("player_data").get(player_steamid).get("is_to_be_obliterated") is True:
                    player_object.is_online = False
                    player_object.is_logging_in = False
                    self.chrani_bot.dom["bot_data"]["player_data"][player_steamid]["is_online"] = False
                    self.chrani_bot.dom["bot_data"]["player_data"][player_steamid]["is_logging_in"] = False
                    players_to_obliterate.append(player_object)

            for player_object in players_to_obliterate:
                self.chrani_bot.socketio.emit('remove_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                self.chrani_bot.socketio.emit('remove_leaflet_markers', player_object.get_leaflet_marker_json(), namespace='/chrani-bot/public')
                self.chrani_bot.players.remove(player_object)

            self.last_execution_time = time.time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        self.cleanup()
        logger.debug("player observer thread has stopped")
