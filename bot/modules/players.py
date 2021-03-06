from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.modules.logger import logger
import json
import os
import pathlib2

from bot.objects.player import Player


class Players(object):

    chrani_bot = object

    root = str
    extension = str

    players_dict = dict

    def __init__(self, chrani_bot):
        self.chrani_bot = chrani_bot
        self.root = "data/{db}/players".format(db=args_dict['Database-file'])
        self.extension = "json"

        self.players_dict = {}

    def player_left_the_world(self, m):
        bot = self.chrani_bot
        try:
            player_steamid = m.group("player_steamid")
            command = m.group("command")
            if command != "Teleport":
                player_object = self.get_by_steamid(player_steamid)
                spawning_player = {
                    "thread": bot.dom["bot_data"]["active_threads"]["player_observer"][player_steamid],
                    "player_object": player_object
                }

                return spawning_player

            raise KeyError

        except KeyError:
            pass

    def load(self, steamid):
        try:
            with open("{}/{}.{}".format(self.root, str(steamid), self.extension)) as file_to_read:
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
                if filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        try:
                            player_dict = byteify(json.load(file_to_read))
                        except ValueError:
                            continue

                        player_dict['health'] = 0
                        player_dict['is_online'] = False
                        player_dict['is_logging_in'] = False
                        players_dict[player_dict['steamid']] = Player(**player_dict)
                        self.chrani_bot.dom["bot_data"]["player_data"][player_dict['steamid']] = player_dict

        self.players_dict = players_dict

    def entityid_to_steamid(self, entityid):
        for steamid, player_object in self.players_dict.iteritems():
            if player_object.entityid == entityid:
                return steamid

        return False

    def name_to_steamid(self, name):
        for steamid, player_object in self.players_dict.iteritems():
            if player_object.name == name:
                return steamid

        return False

    def get_by_steamid(self, steamid):
        try:
            return self.players_dict[steamid]
        except KeyError:
            raise


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

    def remove(self, player_object):
        filename = "{}/{}.{}".format(self.root, player_object.steamid, self.extension)
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
                "permission_levels": self.chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("permission_levels", []),
                "pos_x": self.chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("pos_x", 0),
                "pos_y": self.chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("pos_y", 0),
                "pos_z": self.chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("pos_z", 0),
                "steamid": player_object.steamid,
                "entityid": player_object.entityid,
                "region": player_object.region,
                "country_code": player_object.country_code,
                "authenticated": player_object.authenticated,
                "is_banned": player_object.is_banned,
                "is_muted": player_object.is_muted,
                "last_teleport": player_object.last_teleport,
                "last_responsive": player_object.last_responsive,
                "last_seen": player_object.last_seen,
                "playerfriends_list": player_object.playerfriends_list,
            }

        except Exception as e:
            logger.debug("Preparing player-record for player {} failed: {}".format(player_object.steamid, e.message))
            dict_to_save = {}  # this will fail the next
        try:
            pathlib2.Path(self.root).mkdir(parents=True, exist_ok=True)
            with open("{}/{}.{}".format(self.root, dict_to_save['steamid'], self.extension), 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Saved player-record for player {}.".format(player_object.steamid))
        except Exception as e:
            logger.debug("Saving player-record for player {} failed: {}".format(player_object.steamid, e.message))
            pass
