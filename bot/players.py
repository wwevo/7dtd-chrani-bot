from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.logger import logger
import json
import os
from bot.player import Player


class Players(object):
    """ made this to hold all system relevant functions regarding locations

    used to store persistent data, for now in a pickled shelve, but we can easily use any db here.
    at no other point in the project should read or write functions be performed!

    files will be named <steamid>.shelve,
    except for system locations like the lobby, they will be shelved in system.shelve
    """

    root = str
    prefix = str

    players_dict = dict

    def __init__(self):
        self.root = 'data/players/'
        self.prefix = args_dict['Database-file']
        self.players_dict = {}

    # def load_all(self):
    #     all_players_dict = {}
    #     for root, dirs, files in os.walk(self.root):
    #         for filename in files:
    #             if filename.startswith(self.prefix) and filename.endswith('.json'):
    #                 with open(self.root + filename) as file_to_read:
    #                     player_dict = byteify(json.load(file_to_read))
    #                     player_dict['health'] = 0
    #                     all_players_dict[player_dict['steamid']] = Player(**player_dict)
    #
    #     return all_players_dict

    def get(self, player_steamid):
        try:
            player = self.players_dict[player_steamid]
            return player
        except KeyError:
            raise

    def load(self, steamid):
        try:
            with open(self.root + self.prefix + '_' + str(steamid) + '.json') as file_to_read:
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
        try:
            filename = self.root + self.prefix + '_' + player_object.steamid + '.json'
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError, e:
                    logger.error("Error: {} - {}.".format(e.filename, e.strerror))
            else:
                logger.error("Sorry, I can not find {} file.".format(filename))
            pass
        except KeyError:
            raise

    def save(self, player_object):
        dict_to_save = player_object.__dict__
        with open(self.root + self.prefix + '_' + dict_to_save['steamid'] + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
