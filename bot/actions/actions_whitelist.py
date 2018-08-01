import re
import urllib

from bot.assorted_functions import ObjectView
from bot.modules.logger import logger
import common


def add_player_to_whitelist(bot, source_player, target_player, command):
    try:
        p = re.search(r"add\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sto whitelist", command)
        if p:
            steamid_to_whitelist = p.group("steamid")
            entityid_to_whitelist = p.group("entityid")
            if steamid_to_whitelist is None:
                steamid_to_whitelist = bot.players.entityid_to_steamid(entityid_to_whitelist)
                if steamid_to_whitelist is False:
                    raise KeyError

            try:
                target_player = bot.players.get_by_steamid(steamid_to_whitelist)
                player_dict_to_whitelist = {
                    "steamid": target_player.steamid,
                    "name": target_player.name
                }
            except KeyError:
                player_dict_to_whitelist = {
                    "steamid": steamid_to_whitelist,
                    "name": 'unknown offline player'
                }

            if not bot.whitelist.add(target_player, player_dict_to_whitelist):
                bot.tn.send_message_to_player(target_player, "could not find a player with steamid {}".format(steamid_to_whitelist), color=bot.chat_colors['warning'])
                return False

            bot.tn.send_message_to_player(target_player, "you have whitelisted {}".format(player_dict_to_whitelist["name"]), color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "add player",
        "usage": "/add player <steamid/entityid> to whitelist"
    },
    "action": add_player_to_whitelist,
    "env": "(self, command)",
    "group": "whitelist",
    "essential": False
})


def remove_player_from_whitelist(bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfrom whitelist", command)
        if p:
            steamid_to_dewhitelist = p.group("steamid")
            entityid_to_dewhitelist = p.group("entityid")
            if steamid_to_dewhitelist is None:
                steamid_to_dewhitelist = bot.players.entityid_to_steamid(entityid_to_dewhitelist)
                if steamid_to_dewhitelist is False:
                    raise KeyError

            player_dict = ObjectView
            try:
                player_object_to_dewhitelist = bot.players.get_by_steamid(steamid_to_dewhitelist)
                player_dict.steamid = player_object_to_dewhitelist.steamid
                player_dict.name = player_object_to_dewhitelist.name
            except KeyError:
                player_dict.steamid = steamid_to_dewhitelist
                player_dict.name = 'unknown offline player'
                player_object_to_dewhitelist = player_dict

            if bot.whitelist.remove(player_object_to_dewhitelist):
                bot.tn.send_message_to_player(player_object_to_dewhitelist, "you have been de-whitelisted by {}".format(target_player.name), color=bot.chat_colors['alert'])
            else:
                bot.tn.send_message_to_player(target_player, "could not find a player with steamid '{}' on the whitelist".format(steamid_to_dewhitelist), color=bot.chat_colors['warning'])
                return False
            bot.tn.send_message_to_player(target_player, "you have de-whitelisted {}".format(player_object_to_dewhitelist.name), color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "remove player",
        "usage": "/remove player <steamid/entityid> from whitelist"
    },
    "action": remove_player_from_whitelist,
    "env": "(self, command)",
    "group": "whitelist",
    "essential": False
})


def activate_whitelist(bot, source_player, target_player, command):
    try:
        bot.whitelist.activate()
        bot.tn.say("Whitelist is in effect! Feeling safer already :)", color=bot.chat_colors['alert'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "activate whitelist",
        "usage": "/activate whitelist"
    },
    "action": activate_whitelist,
    "env": "(self)",
    "group": "whitelist",
    "essential": False
})


def deactivate_whitelist(bot, source_player, target_player, command):
    try:
        bot.whitelist.deactivate()
        bot.tn.say("Whitelist has been disabled. We are feeling adventureous :)", color=bot.chat_colors['alert'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "deactivate whitelist",
        "usage": "/deactivate whitelist"
    },
    "action": deactivate_whitelist,
    "env": "(self)",
    "group": "whitelist",
    "essential": False
})
