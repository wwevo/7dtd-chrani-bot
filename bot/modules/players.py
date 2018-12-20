import __main__  # my ide throws a warning here, but it works oO
from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.modules.logger import logger
import json
import os

from bot.objects.player import Player


class Players(object):

    root = str
    prefix = str
    extension = str

    players_dict = dict

    def __init__(self):
        self.root = 'data/players'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.players_dict = {}

    def player_left_the_world(self, m):
        bot = __main__.chrani_bot
        try:
            player_steamid = m.group("player_steamid")
            command = m.group("command")
            if command != "Teleport":
                player_object = self.get_by_steamid(player_steamid)
                spawning_player = {
                    "thread": bot.player_observer.active_player_threads_dict[player_steamid]["thread"],
                    "player_object": player_object
                }

                return spawning_player

            raise KeyError

        except KeyError:
            pass

    def load(self, steamid):
        try:
            with open("{}/{}_{}.{}".format(self.root, self.prefix, str(steamid), self.extension)) as file_to_read:
                player_dict = byteify(json.load(file_to_read))
                player_object = Player(**player_dict)
                return player_object
        except IOError as e:
            logger.debug("{error} for {file}".format(error=e.strerror, file=e.filename))

        raise KeyError

    def load_all(self):
        players_dict = {}
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        try:
                            player_dict = byteify(json.load(file_to_read))
                        except ValueError:
                            continue

                        player_dict['health'] = 0
                        players_dict[player_dict['steamid']] = Player(**player_dict)

        self.players_dict = players_dict

    def entityid_to_steamid(self, entityid):
        for steamid, player_object in self.players_dict.iteritems():
            if player_object.entityid == entityid:
                return steamid

        return False

    def get_by_steamid(self, steamid):
        try:
            return self.players_dict[steamid]
        except KeyError:
            raise

        # try:
        #     return self.load(steamid)
        # except KeyError:
        #     raise

    def get_all_players(self, get_online_only=False):
        try:
            players_to_list = []
            for steamid, player_object_to_list in self.players_dict.iteritems():
                if str(steamid) == "system":
                    continue
                elif not get_online_only:
                    players_to_list.append(player_object_to_list)
                elif player_object_to_list.is_online:
                    players_to_list.append(player_object_to_list)

            return players_to_list

        except KeyError:
            raise

    def upsert(self, player_object, save=False):
        try:
            self.players_dict[player_object.steamid] = player_object
            if save:
                self.save(player_object)
                return True
        except Exception as e:
            logger.exception(e)

        return False

    def get_leaflet_marker_json(self, player_objects):
        player_list = []
        for player in player_objects:

            if not isinstance(player.pos_x, float) or not isinstance(player.pos_y, float) or not isinstance(player.pos_z, float):
                continue

            player_list.append({
                "id": "{}".format(player.steamid),
                "owner": player.steamid,
                "identifier": player.name,
                "name": player.name,
                "radius": 3,
                "pos_x": player.pos_x,
                "pos_y": player.pos_y,
                "pos_z": player.pos_z,
                "online": player.is_online,
                "shape": "icon",
                "type": "icon",
                "layerGroup": "players"
            })

        return player_list

    def remove(self, player_object):
        filename = "{}/{}_{}.{}".format(self.root, self.prefix, player_object.steamid, self.extension)
        if os.path.isfile(filename):
            try:
                os.remove(filename)
                del self.players_dict[player_object.steamid]
                return True
            except Exception as e:
                logger.exception(e.message)

        return False

    def save(self, player_object):
        try:
            dict_to_save = {
                "id": player_object.id,
                "name": player_object.name,
                "permission_levels": player_object.permission_levels,
                "steamid": player_object.steamid,
                "entityid": player_object.entityid,
                "region": player_object.region,
                "country_code": player_object.country_code,
                "authenticated": player_object.authenticated,
                "is_banned": player_object.is_banned,
                "is_muted": player_object.is_manually_muted,
                "last_teleport": player_object.last_teleport,
                "last_responsive": player_object.last_responsive,
                "last_seen": player_object.last_seen,
                "playerfriends_list": player_object.playerfriends_list,
            }

        except Exception as e:
            logger.debug("Preparing player-record for player {} failed: {}".format(player_object.steamid, e.message))
            dict_to_save = {}  # this will fail the next
        try:
            with open("{}/{}_{}.{}".format(self.root, self.prefix, dict_to_save['steamid'], self.extension), 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Saved player-record for player {}.".format(player_object.steamid))
        except Exception as e:
            logger.debug("Saving player-record for player {} failed: {}".format(player_object.steamid, e.message))
            pass
