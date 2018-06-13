from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.logger import logger
import json
import os


class Whitelist(object):

    root = str
    prefix = str
    extension = str

    whitelisted_players_dict = dict

    whitelist_active = bool

    def __init__(self):
        self.root = 'data/whitelist'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.whitelisted_players_dict = {}
        self.whitelist_active = False

    def load_all(self):
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        try:
                            whitelisted_player = byteify(json.load(file_to_read))
                            self.whitelisted_players_dict[whitelisted_player['steamid']] = whitelisted_player
                        except ValueError:
                            pass

    def is_active(self):
        return self.whitelist_active

    def activate(self):
        self.whitelist_active = True

    def deactivate(self):
        self.whitelist_active = False

    def add(self, player_object, player_dict_to_whitelist, save=False):
        try:
            is_in_dict = self.whitelisted_players_dict[player_dict_to_whitelist["steamid"]]
        except Exception:
            self.whitelisted_players_dict.update({player_dict_to_whitelist["steamid"]: {
                'name': player_dict_to_whitelist["name"],
                'whitelisted_by': player_object.steamid
            }})
        if save:
            self.save(player_dict_to_whitelist)
            return True

    def remove(self, player_object_to_dewhitelist):
        try:
            filename = "{}/{}_{}.{}".format(self.root, self.prefix, player_object_to_dewhitelist.steamid, self.extension)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    del self.whitelisted_players_dict[player_object_to_dewhitelist.steamid]
                    return True
                except OSError, e:
                    logger.exception(e)
            else:
                logger.exception(e)
                return False
        except KeyError:
            raise

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
        dict_to_save = player_object
        with open("{}/{}_{}.{}".format(self.root, self.prefix, dict_to_save["steamid"], self.extension), 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
