from command_line_args import args_dict
from byteify import byteify
import json
import os
from player import Player


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
        pass

    def load_all(self, online_players_dict=None):
        if online_players_dict:  # for now we only implement this one ^^
            ids = online_players_dict.keys()
            for root, dirs, files in os.walk(self.root):
                for filename in files:
                    if any(ext in filename for ext in ids):
                        if filename.startswith(self.prefix) and filename.endswith('.json'):
                            with open(self.root + filename) as file_to_read:
                                player_dict = byteify(json.load(file_to_read))
                                self.players_dict[player_dict['steamid']] = Player(**player_dict)

    def get(self, player_steamid):
        try:
            player = self.players_dict[player_steamid]
            return player
        except KeyError:
            raise

    def load(self, steamid):
        try:
            with open(self.root + self.prefix + '_' + str(steamid) + '.json') as file_to_read:
                player_dict = json.load(file_to_read)
                player_object = Player(**player_dict)
                self.players_dict[str(player_dict['steamid'])] = player_object
                return player_object
        except:
            raise KeyError

    def upsert(self, player_object, save=False):
        self.players_dict[player_object.steamid] = player_object
        if save:
            self.save(player_object)

    def remove(self):
        pass

    def save(self, player_object):
        dict_to_save = player_object.__dict__
        with open(self.root + self.prefix + '_' + dict_to_save['steamid'] + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write)
