from bot.assorted_functions import byteify
import json
from bot.modules.logger import logger

from bot.command_line_args import args_dict
from bot.objects.player import Player
import pathlib2


class Permissions(object):

    chrani_bot = object
    root = str
    extension = str

    available_actions_dict = dict

    permission_levels_list = list
    action_permissions_dict = dict

    def __init__(self, chrani_bot, permission_levels_list):
        self.chrani_bot = chrani_bot
        self.root = "data/{db}".format(db=args_dict['Database-file'])
        self.extension = "json"
        self.available_actions_dict = {}
        self.action_permissions_dict = {}
        self.permission_levels_list = permission_levels_list

    def player_has_permission(self, player_object, action_identifier=None, action_group=None):
        if player_object.steamid == 'system':
            return True
        if player_object.steamid in self.chrani_bot.settings.get_setting_by_name(name='webinterface_admins'):
            return True
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
                return True  # as in no permission required

    def load_all(self, player_actions_list):
        self.player_actions_list = player_actions_list
        filename = "{}/permissions.{}".format(self.root, self.extension)
        try:
            with open(filename) as file_to_read:
                self.action_permissions_dict = byteify(json.load(file_to_read))
        except IOError:  # no permissions file available
            pass

        bot = self.chrani_bot
        player_dict = {
            "entityid": "0",
            "name": "system",
            "steamid": "system",
            "pos_x": 0.0,
            "pos_y": 0.0,
            "pos_z": 0.0,
            "is_online": False
        }

        player_object = Player(**player_dict)
        bot.players.upsert(player_object)

        self.update_permissions_file(player_actions_list)

    def update_permissions_file(self, player_actions_list):
        filename = '{}/permissions.{}'.format(self.root, self.extension)

        available_actions_dict = {}
        for player_action in player_actions_list:
            if player_action["essential"] is False:  # quick hack to get some system-functions in ^^
                # if it were 'True', it would be a system action not requiring permission, they are available to all
                try:
                    # see if this exact action already has permission groups attached
                    permission_groups = self.action_permissions_dict[player_action["group"]][getattr(player_action["action"], 'func_name')]
                except KeyError:
                    permission_groups = None

                try:
                    # permission group already exists, update it
                    available_actions_dict[player_action["group"]].update({getattr(player_action["action"], 'func_name'): permission_groups})
                except Exception:
                    # the whole permission group is new, set it up!
                    available_actions_dict[player_action["group"]] = {getattr(player_action["action"], 'func_name'): permission_groups}
        try:
            self.save(available_actions_dict)
            return filename
        except Exception:
            raise IOError

    def save(self, available_actions_dict):
        dict_to_save = available_actions_dict
        filename = '{}/permissions.{}'.format(self.root, self.extension)
        try:
            pathlib2.Path(self.root).mkdir(parents=True, exist_ok=True)
            with open(filename, 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Updated permissions file.")
        except:
            logger.exception("Updating permissions file failed.")
