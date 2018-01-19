from command_line_args import args_dict
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

    root = 'data/players/'
    prefix = args_dict['Database-file']

    players_dict = {}

    def __init__(self, online_players_dict):
        self.load_all(online_players_dict)

    def load_all(self, online_players_dict):
        if online_players_dict:
            ids = online_players_dict.keys()
            for root, dirs, files in os.walk(self.root):
                for file in files:
                    if any(ext in file for ext in ids):
                        if file.startswith(self.prefix) and file.endswith('.json'):
                            with open(self.root + file) as file_to_read:
                                player_dict = json.load(file_to_read)
                                self.players_dict[str(player_dict['steamid'])] = Player(**player_dict)

    def load(self, steamid):
        try:
            with open(self.root + self.prefix + '_' + str(steamid) + '.json') as file_to_read:
                player_dict = json.load(file_to_read)
                self.players_dict[str(player_dict['steamid'])] = Player(**player_dict)
        except:
            pass

    def upsert(self, player_dict, save=False):
        if player_dict['steamid'] in self.players_dict:
            self.players_dict[player_dict['steamid']].update(**player_dict)
        else:
            self.players_dict[player_dict['steamid']] = Player(**player_dict)
        if save:
            self.save(player_dict)

    def get(self, player_steamid):
        try:
            player = self.players_dict[player_steamid]
            return player
        except KeyError:
            return False

    def remove(self):
        pass

    def save(self, player):
        dict_to_save = vars(player)
        # dict_to_save['authenticated'] = player.authenticated
        with open(self.root + self.prefix + '_' + dict_to_save['steamid'] + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write)
