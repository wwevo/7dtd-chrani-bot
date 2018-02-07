from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.logger import logger
import json
import os


class Whitelist(object):

    root = str
    prefix = str

    whitelisted_players_dict = dict

    whitelist_active = bool

    def __init__(self):
        self.root = 'data/whitelist/'
        self.prefix = args_dict['Database-file']
        self.whitelisted_players_dict = {}
        self.whitelist_active = False

    def load_all(self):
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith('.json'):
                    with open(self.root + filename) as file_to_read:
                        whitelisted_player = byteify(json.load(file_to_read))
                        self.whitelisted_players_dict[whitelisted_player['steamid']] = whitelisted_player

    def is_active(self):
        return self.whitelist_active

    def activate(self):
        self.whitelist_active = True

    def deactivate(self):
        self.whitelist_active = False

    def upsert(self, player_object, player_object_to_whitelist, save=False):
        try:
            is_in_dict = self.whitelisted_players_dict[player_object_to_whitelist.steamid]
        except Exception:
            self.whitelisted_players_dict.update({player_object_to_whitelist.steamid: {
                'name': player_object_to_whitelist.name,
                'whitelisted_by': player_object.steamid
            }})
        if save:
            self.save(player_object_to_whitelist)
            return True

    def player_is_allowed(self, player_object):
        try:
            is_in_dict = self.whitelisted_players_dict[player_object.steamid]
            return True
        except KeyError:
            try:
                return [i for i in ["admin", "mod", "donator"] if i in player_object.permission_levels]
            except Exception:
                return False

    def save(self, player_object):
        dict_to_save = vars(player_object)
        with open(self.root + self.prefix + '_' + dict_to_save['steamid'] + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
