from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.modules.logger import logger
from threading import Event
from bot.player_observer import PlayerObserver

import json
import os
import re
from bot.objects.player import Player


class Players(object):

    root = str
    prefix = str
    extension = str

    filename = str

    players_dict = dict
    all_players_dict = dict

    poll_listplayerfriends_interval = float

    def __init__(self):
        self.root = 'data/players'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.players_dict = {}
        self.poll_listplayerfriends_interval = 30
        self.load_all()

    def manage_online_players(self, bot, listplayers_dict):
        def poll_players():
            online_players_dict = {}
            listplayers_result = bot.poll_tn.listplayers()
            for m in re.finditer(bot.match_types_system["listplayers_result_regexp"], listplayers_result):
                online_players_dict.update({m.group(16): {
                    "entityid": m.group(1),
                    "name":     str(m.group(2)),
                    "pos_x":    float(m.group(3)),
                    "pos_y":    float(m.group(4)),
                    "pos_z":    float(m.group(5)),
                    "rot_x":    float(m.group(6)),
                    "rot_y":    float(m.group(7)),
                    "rot_z":    float(m.group(8)),
                    "remote":   bool(m.group(9)),
                    "health":   int(m.group(10)),
                    "deaths":   int(m.group(11)),
                    "zombies":  int(m.group(12)),
                    "players":  int(m.group(13)),
                    "score":    m.group(14),
                    "level":    m.group(15),
                    "steamid":  m.group(16),
                    "ip":       str(m.group(17)),
                    "ping":     int(m.group(18))
                }})
            return online_players_dict

        # get all currently online players and store them in a dictionary
        last_listplayers_dict = listplayers_dict
        listplayers_dict = poll_players()

        # prune players not online anymore
        for player in set(self.players_dict) - set(listplayers_dict.keys()):
            del self.players_dict[player]

        # create new player entries / update existing ones
        for player_steamid, player_dict in listplayers_dict.iteritems():
            try:
                player_object = self.get_by_steamid(player_steamid)
                # player is already online and needs updating
                player_object.update(**player_dict)
                if last_listplayers_dict != listplayers_dict:  # but only if they have changed at all!
                    """ we only update this if things have changed since this poll is slow and might
                    be out of date. Any teleport issued by the bot or a player would generate more accurate data
                    If it HAS changed it is by all means current and can be used to update the object.
                    """
                    self.upsert(player_object)
            except KeyError:  # player has just come online
                try:
                    player_object = self.load(player_steamid)
                    # player has a file on disc, update database!
                    player_object.update(**player_dict)
                    self.upsert(player_object)
                except KeyError:  # player is totally new, create file!
                    player_object = Player(**player_dict)
                    self.upsert(player_object, save=True)
            # there should be a valid object state here now ^^

        """ handle player-threads """
        for player_steamid, player_object in self.players_dict.iteritems():
            """ start player_observer_thread for each player not already being observed """
            if player_steamid not in bot.active_player_threads_dict:
                player_observer_thread_stop_flag = Event()
                player_observer_thread = PlayerObserver(player_observer_thread_stop_flag, bot, str(player_steamid))  # I'm passing the bot (self) into it to have easy access to it's variables
                player_observer_thread.name = player_steamid  # nice to have for the logs
                player_observer_thread.isDaemon()
                player_observer_thread.trigger_action(player_object, "entered the stream")
                player_observer_thread.start()
                bot.active_player_threads_dict.update({player_steamid: {"event": player_observer_thread_stop_flag, "thread": player_observer_thread}})

        for player_steamid in set(bot.active_player_threads_dict) - set(self.players_dict.keys()):
            """ prune all active_player_threads from players no longer online """
            active_player_thread = bot.active_player_threads_dict[player_steamid]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
            del bot.active_player_threads_dict[player_steamid]

        return listplayers_dict

    def load_all(self):
        # TODO: this need to be cached or whatever!
        all_players_dict = {}
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        try:
                            player_dict = byteify(json.load(file_to_read))
                        except ValueError:
                            continue

                        player_dict['health'] = 0
                        all_players_dict[player_dict['steamid']] = Player(**player_dict)

        self.all_players_dict = all_players_dict
        return all_players_dict

    def entityid_to_steamid(self, entityid):
        for steamid, player_object in self.all_players_dict.iteritems():
            if player_object.entityid == entityid:
                return steamid

        return False

    def get_by_steamid(self, steamid):
        try:
            player_object = self.players_dict[steamid]
            return player_object
        except KeyError:
            pass

        try:
            player_object = self.load(steamid)
            return player_object
        except KeyError:
            raise

    def get_online_players(self):
        try:
            active_players_dict = self.players_dict
            players_to_list = []
            for steamid, player_object_to_list in active_players_dict.iteritems():
                players_to_list.append(player_object_to_list)

            return players_to_list

        except KeyError:
            raise

    def get_all_players(self):
        try:
            active_players_dict = self.load_all()
            players_to_list = []
            for steamid, player_object_to_list in active_players_dict.iteritems():
                players_to_list.append(player_object_to_list)

            return players_to_list

        except KeyError:
            raise

    def load(self, steamid):
        try:
            with open("{}/{}_{}.{}".format(self.root, self.prefix, str(steamid), self.extension)) as file_to_read:
                player_dict = byteify(json.load(file_to_read))
                player_object = Player(**player_dict)
                return player_object
        except Exception:
            raise KeyError

    def upsert(self, player_object, save=False):
        try:
            self.players_dict[player_object.steamid] = player_object
            if save:
                self.save(player_object)
        except Exception as e:
            logger.exception(e)

    def remove(self, player_object):
        filename = "{}/{}_{}.{}".format(self.root, self.prefix, player_object.steamid, self.extension)
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logger.exception(e)
                pass
        else:
            return False

    def save(self, player_object):
        dict_to_save = {
            "id": player_object.id,
            "name": player_object.name,
            "permission_levels": player_object.permission_levels,
            "death_x": player_object.death_x,
            "death_y": player_object.death_y,
            "death_z": player_object.death_z,
            "steamid": player_object.steamid,
            "entityid": player_object.entityid,
            "region": player_object.region,
            "country_code": player_object.country_code,
            "authenticated": player_object.authenticated,
            "is_muted": player_object.is_muted,
            "last_teleport": player_object.last_teleport,
            "last_responsive": player_object.last_responsive,
            "playerfriends_list": player_object.playerfriends_list,
        }
        try:
            with open("{}/{}_{}.{}".format(self.root, self.prefix, dict_to_save['steamid'], self.extension), 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Saved player-record for player {}.".format(dict_to_save['steamid']))
        except Exception as e:
            logger.debug("Saving player-record for player {} failed: {}".format(dict_to_save['steamid'], e.message))
            pass
