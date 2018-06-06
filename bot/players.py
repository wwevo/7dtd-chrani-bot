from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.logger import logger

import json
import os
from bot.player import Player


class Players(object):

    root = str
    prefix = str
    extension = str

    filename = str

    players_dict = dict

    def __init__(self):
        self.root = 'data/players'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.players_dict = {}

    def load_all(self):
        # TODO: this need to be cached or whatever!
        all_players_dict = {}
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        player_dict = byteify(json.load(file_to_read))
                        player_dict['health'] = 0
                        all_players_dict[player_dict['steamid']] = Player(**player_dict)

        return all_players_dict

    def entityid_to_steamid(self, entityid):
        for steamid, player_object in self.players_dict.iteritems():
            if player_object.entityid == entityid:
                return steamid

        all_players_dict = self.load_all()

        for steamid, player_object in all_players_dict.iteritems():
            if player_object.entityid == entityid or player_object.id == entityid:
                return steamid

        return False

    def get(self, steamid):
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
            logger.error(e)

    def remove(self, player_object):
        filename = "{}/{}_{}.{}".format(self.root, self.prefix, player_object.steamid, self.extension)
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logger.error("Error: {} - {}.".format(e.filename, e.strerror))
                pass
        else:
            logger.error("Sorry, I can not find {} file.".format(filename))

    def save(self, player_object):
        dict_to_save = player_object.__dict__
        with open("{}/{}_{}.{}".format(self.root, self.prefix, dict_to_save['steamid'], self.extension), 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
