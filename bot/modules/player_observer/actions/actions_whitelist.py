import re
from bot.assorted_functions import ObjectView
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def add_player_to_whitelist(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"add\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>([0-9]{0,7})))\s(?P<command>.+)", command)
        if p and p.group("command") == "to whitelist":
            response_messages = ResponseMessage()
            steamid_to_whitelist = p.group("steamid")
            entityid_to_whitelist = p.group("entityid")
            if steamid_to_whitelist is None:
                steamid_to_whitelist = chrani_bot.players.entityid_to_steamid(entityid_to_whitelist)
                if steamid_to_whitelist is False:
                    raise KeyError

            try:
                target_player = chrani_bot.players.get_by_steamid(steamid_to_whitelist)
                player_dict_to_whitelist = {
                    "steamid": target_player.steamid,
                    "name": target_player.name,
                    "is_online": False
                }
                response_messages.add_message("adding known player {}".format(target_player.name), True)
            except KeyError:
                player_dict_to_whitelist = {
                    "steamid": steamid_to_whitelist,
                    "name": 'unknown offline player',
                    "is_online": False
                }
                response_messages.add_message("adding unknown player", True)

            if chrani_bot.whitelist.add(source_player, player_dict_to_whitelist, save=True):
                chrani_bot.socketio.emit('refresh_player_whitelist', {"steamid": player_dict_to_whitelist["steamid"], "entityid": None}, namespace='/chrani-bot/public')
                message = "you have whitelisted {}".format(player_dict_to_whitelist["name"])
                if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", source_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                response_messages.add_message(message, True)
            else:
                message = "could not find a player with steamid {}".format(steamid_to_whitelist)
                if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", source_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "add player",
        "usage": "/add player <steamid/entityid> to whitelist"
    },
    "action": add_player_to_whitelist,
    "group": "whitelist",
    "essential": False
})


def remove_player_from_whitelist(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>([0-9]{0,7})))\s(?P<command>.+)", command)
        if p and p.group("command") == "from whitelist":
            response_messages = ResponseMessage()
            steamid_to_dewhitelist = p.group("steamid")
            entityid_to_dewhitelist = p.group("entityid")
            if steamid_to_dewhitelist is None:
                steamid_to_dewhitelist = chrani_bot.players.entityid_to_steamid(entityid_to_dewhitelist)
                if steamid_to_dewhitelist is False:
                    raise KeyError

            player_dict = ObjectView
            try:
                player_object_to_dewhitelist = chrani_bot.players.get_by_steamid(steamid_to_dewhitelist)
                player_dict.steamid = player_object_to_dewhitelist.steamid
                player_dict.name = player_object_to_dewhitelist.name
                response_messages.add_message("removing known player {}".format(player_dict.name), True)
            except KeyError:
                player_dict.steamid = steamid_to_dewhitelist
                player_dict.name = 'unknown offline player'
                player_object_to_dewhitelist = player_dict
                response_messages.add_message("removing unknown player", True)

            if chrani_bot.whitelist.remove(player_object_to_dewhitelist):
                message = "you have been de-whitelisted by {}".format(target_player.name)
                if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object_to_dewhitelist, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, True)

                message = "you have de-whitelisted {}".format(player_object_to_dewhitelist.name)
                if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))

                chrani_bot.socketio.emit('refresh_player_whitelist', {"steamid": player_object_to_dewhitelist.steamid, "entityid": player_object_to_dewhitelist.entityid}, namespace='/chrani-bot/public')
            else:
                message = "could not find a player with steamid '{}' on the whitelist".format(steamid_to_dewhitelist)
                if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            chrani_bot.socketio.emit('refresh_whitelist', '', namespace='/chrani-bot/public')

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "remove player",
        "usage": "/remove player <steamid/entityid> from whitelist"
    },
    "action": remove_player_from_whitelist,
    "group": "whitelist",
    "essential": False
})


def activate_whitelist(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        chrani_bot.whitelist.activate()
        chrani_bot.socketio.emit('refresh_whitelist', '', namespace='/chrani-bot/public')
        chrani_bot.socketio.emit('refresh_player_table', '', namespace='/chrani-bot/public')
        message = "Whitelist is in effect! Feeling safer already :)"
        if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
        response_messages.add_message(message, True)
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "activate whitelist",
        "usage": "/activate whitelist"
    },
    "action": activate_whitelist,
    "group": "whitelist",
    "essential": False
})


def deactivate_whitelist(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        chrani_bot.whitelist.deactivate()
        chrani_bot.socketio.emit('refresh_whitelist', '', namespace='/chrani-bot/public')
        chrani_bot.socketio.emit('refresh_player_table', '', namespace='/chrani-bot/public')
        message = "Whitelist has been disabled. We are feeling adventureous :)"
        if chrani_bot.dom.get("bot_flags").get("bot_has_working_environment", False):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
        response_messages.add_message(message, True)
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "deactivate whitelist",
        "usage": "/deactivate whitelist"
    },
    "action": deactivate_whitelist,
    "group": "whitelist",
    "essential": False
})
