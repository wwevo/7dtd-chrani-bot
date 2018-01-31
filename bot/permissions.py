from command_line_args import args_dict
from bot.byteify import byteify

import json, os


class Permissions(object):

    root = str
    prefix = str

    player_actions_list = list
    permission_levels_list = list

    available_actions_dict = dict

    def __init__(self, player_actions_list, permission_levels_list):
        self.root = 'data/permissions'
        self.prefix = args_dict['Database-file']
        self.permission_levels_list = permission_levels_list
        self.player_actions_list = player_actions_list
        self.available_actions_dict = {}

    def player_has_permission(self, player_object):
        pass

    def create_permissions_file(self):
        filename = '{}/{}_permissions.json'.format(self.root, self.prefix)
        if os.path.isfile(filename):  # already exists, abort! this is just for first setup
            raise IOError

        available_actions_dict = {}
        for player_action in self.player_actions_list:
            try:
                available_actions_dict[player_action[4]].update({getattr(player_action[2], 'func_name'): ['all']})
            except Exception:
                available_actions_dict[player_action[4]] = {getattr(player_action[2], 'func_name'): ['all']}
        try:
            self.save(available_actions_dict)
            return filename
        except Exception:
            raise IOError

    def save(self, available_actions_dict):
        dict_to_save = available_actions_dict
        filename = '{}/{}_permissions.json'.format(self.root, self.prefix)
        with open(filename, 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
