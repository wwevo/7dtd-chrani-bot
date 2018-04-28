from assorted_functions import byteify
import json
import os

from bot.command_line_args import args_dict


class Permissions(object):

    root = str
    prefix = str

    player_actions_list = list
    permission_levels_list = list
    action_permissions_dict = dict

    available_actions_dict = dict

    def __init__(self, player_actions_list, permission_levels_list):
        self.root = 'data/permissions'
        self.prefix = args_dict['Database-file']
        self.permission_levels_list = permission_levels_list
        self.player_actions_list = player_actions_list
        self.available_actions_dict = {}
        self.action_permissions_dict = {}

    def load_all(self):
        filename = "{}/{}_permissions.json".format(self.root, self.prefix)
        try:
            with open(filename) as file_to_read:
                self.action_permissions_dict = byteify(json.load(file_to_read))
            self.upgrade_permissions_file()
        except IOError:  # no permissions file available
            self.create_permissions_file()

    def player_has_permission(self, player_object, action_identifier=None, action_group=None):
        if action_group is None:
            for group in self.action_permissions_dict.iteritems():
                pass
        if isinstance(action_group, str):
            try:
                allowed_player_groups = self.action_permissions_dict[action_group][action_identifier]
                if any((True for x in player_object.permission_levels if x in allowed_player_groups)) is True:
                    return True
                else:
                    return allowed_player_groups
            except (KeyError, TypeError):
                return True  # for now

    def create_permissions_file(self):
        filename = '{}/{}_permissions.json'.format(self.root, self.prefix)
        if os.path.isfile(filename):  # already exists, abort! this is just for first setup
            raise IOError

        available_actions_dict = {}
        for player_action in self.player_actions_list:
            try:
                available_actions_dict[player_action[4]].update({getattr(player_action[2], 'func_name'): None})
            except Exception:
                available_actions_dict[player_action[4]] = {getattr(player_action[2], 'func_name'): None}
        try:
            self.save(available_actions_dict)
            return filename
        except Exception:
            raise IOError

    def upgrade_permissions_file(self):
        filename = '{}/{}_permissions.json'.format(self.root, self.prefix)
        if not os.path.isfile(filename):  # does not already exists, abort!
            raise IOError

        available_actions_dict = self.action_permissions_dict
        for player_action in self.player_actions_list:
            try:
                if getattr(player_action[2], 'func_name') in available_actions_dict[player_action[4]]:
                    pass
                else:
                    available_actions_dict[player_action[4]].update({getattr(player_action[2], 'func_name'): None})
            except Exception:
                try:
                    available_actions_dict[player_action[4]] = {getattr(player_action[2], 'func_name'): None}
                except IndexError:
                    """ you will be getting index errors if you fuck up variables, like adding an action module with, instead of +"""
                    pass

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
