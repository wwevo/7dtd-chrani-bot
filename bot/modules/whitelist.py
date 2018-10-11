import __main__
from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
from bot.modules.logger import logger
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
        is_in_dict = False
        try:
            is_in_dict = self.whitelisted_players_dict[player_dict_to_whitelist["steamid"]]
        except:
            self.whitelisted_players_dict.update({player_dict_to_whitelist["steamid"]: {
                'name': player_dict_to_whitelist["name"],
                'whitelisted_by': player_object.steamid
            }})

        if save and not is_in_dict:
            self.save(player_dict_to_whitelist)

        return True

    def remove(self, player_object_to_dewhitelist):
        try:
            filename = "{}/{}_{}.{}".format(self.root, self.prefix, player_object_to_dewhitelist.steamid, self.extension)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    del self.whitelisted_players_dict[player_object_to_dewhitelist.steamid]
                    logger.debug("Player {} removed from whitelist.".format(player_object_to_dewhitelist.steamid))
                    return True
                except OSError, e:
                    logger.exception(e)
            else:
                logger.debug("whitelist removal of player {} failed".format(player_object_to_dewhitelist.steamid))
                return False
        except KeyError:
            raise

    def player_is_allowed(self, player_object):
        """Checks if a player may play while whitelist is active

        checks if the player has been manually whitelisted
        checks if player has an auto-whitelisted role

        returns False if player is not allowed

        Keyword arguments:
        self -- the bot
        player_object -- player to check
        """
        bot = __main__.chrani_bot
        authentication_groups = bot.settings.get_setting_by_name("authentication_groups")
        try:
            is_in_dict = self.whitelisted_players_dict[player_object.steamid]
            return True
        except KeyError:
            try:
                return [i for i in authentication_groups if i in player_object.permission_levels]
            except Exception:
                return False

    def player_is_on_whitelist(self, player_steamid):
        """Checks if a player may play while whitelist is active

        checks if the player has been manually whitelisted
        checks if player has an auto-whitelisted role

        returns False if player is not allowed

        Keyword arguments:
        self -- the bot
        player_object -- player to check
        """
        try:
            is_in_dict = self.whitelisted_players_dict[player_steamid]
            return True
        except KeyError:
            return False

    def save(self, dict_to_save):
        try:
            with open("{}/{}_{}.{}".format(self.root, self.prefix, dict_to_save["steamid"], self.extension), 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Saved player-record {} for whitelisting.".format(dict_to_save["steamid"]))
        except Exception:
            logger.exception("Saving player-record {} for whitelisting failed.".format(dict_to_save["steamid"]))
            return False

        return True
