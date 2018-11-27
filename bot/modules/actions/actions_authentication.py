import re
import common
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger


def on_enter_gameworld(bot, source_player, target_player, command):
    """Will greet an unauthenticated player

    Keyword arguments:
    self -- the bot

    notes:
    does nothing for authenticated players
    """
    try:
        response_messages = ResponseMessage()
        response_messages.add_message("Player {} has been seen in the logs".format(target_player.name), True)

        target_player.is_online = True
        target_player.is_logging_in = False
        bot.players.upsert(target_player, save=True)

        if not target_player.has_permission_level("authenticated"):
            bot.tn.send_message_to_player(target_player, "read the rules on {}".format(bot.settings.get_setting_by_name(name='rules_url')), color=bot.chat_colors['warning'])
            bot.tn.send_message_to_player(target_player, "this is a development server. you can play here, but there's no support or anything really.", color=bot.chat_colors['info'])
            bot.tn.send_message_to_player(target_player, "Enjoy!", color=bot.chat_colors['info'])
            bot.players.upsert(target_player)
            response_messages.add_message("Player {} is now initialized".format(target_player.name), True)

        if command == "entered the world":
            bot.tn.send_message_to_player(target_player, "List your available chat-actions with [{}]{}[-]".format(bot.chat_colors['standard'], common.find_action_help("players", "list actions")), color=bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "EnterMultiplayer",
        "usage": None
    },
    "action": on_enter_gameworld,
    "group": "authentication",
    "essential": True
})


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "found in the world",
        "usage": None
    },
    "action": on_enter_gameworld,
    "group": "authentication",
    "essential": True
})


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "JoinMultiplayer",
        "usage": None
    },
    "action": on_enter_gameworld,
    "group": "authentication",
    "essential": True
})


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "entered the world",
        "usage": None
    },
    "action": on_enter_gameworld,
    "group": "authentication",
    "essential": True
})


def password(bot, source_player, target_player, command):
    """Adds player to permission-group(s) according to the password entered
    will remove authenticated status if the player enters a woing password

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /password <password>

    example:
    /password openup

    notes:
    the password must exist in the password dictionary
    """
    try:
        p = re.search(r"^password\s?(?P<password>\w+)$|^password\s?$", command)
        if p:
            response_messages = ResponseMessage()
            pwd = p.group("password")
            if not pwd:
                message = "No password provided"
                bot.tn.send_message_to_player(target_player, "You have entered no password. Use {}".format(
                    common.find_action_help("authentication", "password")), color=bot.chat_colors['warning'])
                response_messages.add_message(message, False)
            elif pwd not in bot.passwords.values() and not target_player.authenticated:
                message = "Entered a wrong / unknown password"
                bot.tn.send_message_to_player(target_player, "You have entered a wrong password!", color=bot.chat_colors['warning'])
                response_messages.add_message(message, False)
            elif pwd not in bot.passwords.values() and target_player.authenticated:
                target_player.set_authenticated(False)
                message = "Entered a wrong / unknown password"
                response_messages.add_message(message, False)
                target_player.remove_permission_level("authenticated")
                target_player.update()
                message = "You have lost your authentication!"
                response_messages.add_message(message, False)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])
                bot.tn.muteplayerchat(target_player, True)
                bot.players.upsert(target_player, save=True)
                bot.socketio.emit('refresh_permissions', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
            elif pwd in bot.passwords.values():
                bot.tn.muteplayerchat(target_player, False)
                if not target_player.authenticated:
                    message = "{} joined the ranks of literate people. Welcome!".format(target_player.name)
                    response_messages.add_message(message, True)
                    bot.tn.say(message, color=bot.chat_colors['standard'])

                target_player.add_permission_level("authenticated")
                message = "You were added to the group authenticated"
                response_messages.add_message(message, True)

                """ makeshift promotion system """
                # TODO: well, this action should only care about general authentication. things like admin and mod should be handled somewhere else really
                if pwd == bot.passwords['admin']:
                    target_player.add_permission_level("admin")
                    target_player.update()
                    message = "you are an Admin"
                    response_messages.add_message(message, True)
                    bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
                elif pwd == bot.passwords['mod']:
                    target_player.add_permission_level("mod")
                    target_player.update()
                    message = "you are a Moderator"
                    response_messages.add_message(message, True)
                    bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
                elif pwd == bot.passwords['donator']:
                    target_player.add_permission_level("donator")
                    target_player.update()
                    message = "you are a Donator. Thank you <3"
                    response_messages.add_message(message, True)
                    bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])

                bot.socketio.emit('refresh_permissions', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
                bot.players.upsert(target_player, save=True)
            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "password",
        "usage": "/password <password>"
    },
    "action": password,
    "group": "authentication",
    "essential": True
})


def add_player_to_permission_group(bot, source_player, target_player, command):
    """Adds player to permission-group

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /add player <steamid/entityid> to group <group_name>

    example:
    /add player 76561198040658370 to group admin

    notes:
    the group must exist
    """
    try:
        p = re.search(r"add\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sto\sgroup\s(?P<group_name>\w+)", command)
        if p:
            response_messages = ResponseMessage()
            steamid_to_modify = p.group("steamid")
            entityid_to_modify = p.group("entityid")
            if steamid_to_modify is None:
                steamid_to_modify = bot.players.entityid_to_steamid(entityid_to_modify)

            player_exists = False
            try:
                player_object_to_modify = bot.players.get_by_steamid(steamid_to_modify)
                player_exists = True
            except Exception as e:
                if steamid_to_modify is False:
                    message = "Could not find a player to match entityid {}".format(entityid_to_modify)
                    response_messages.add_message(message, False)
                else:
                    message = "could not find a player to match steamid {}".format(steamid_to_modify)
                    response_messages.add_message(message, False)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])

            group_exists = False
            group = str(p.group("group_name"))
            if group in bot.permission_levels_list:
                group_exists = True
            else:
                message = "the group {} does not exist!".format(group)
                response_messages.add_message(message, False)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])

            if player_exists and group_exists:
                player_object_to_modify.add_permission_level(group)
                message = "{} has been added to the group {}".format(player_object_to_modify.name, group)
                response_messages.add_message(message, True)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
                bot.socketio.emit('refresh_permissions', {"steamid": player_object_to_modify.steamid, "entityid": player_object_to_modify.entityid}, namespace='/chrani-bot/public')
                bot.players.upsert(player_object_to_modify, save=True)

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
        "usage": "/add player <steamid/entityid> to group <group name>"
    },
    "action": add_player_to_permission_group,
    "group": "authentication",
    "essential": False
})


def remove_player_from_permission_group(bot, source_player, target_player, command):
    """Removes player from permission-group

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /remove player <steamid/entityid> from group <group_name>

    example:
    /remove player 76561198040658370 from group admin

    notes:
    the group must exist
    """
    try:
        p = re.search(r"remove\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sfrom\sgroup\s(?P<group_name>\w+)", command)
        if p:
            response_messages = ResponseMessage()
            steamid_to_modify = p.group("steamid")
            entityid_to_modify = p.group("entityid")
            if steamid_to_modify is None:
                steamid_to_modify = bot.players.entityid_to_steamid(entityid_to_modify)

            player_exists = False
            try:
                player_object_to_modify = bot.players.get_by_steamid(steamid_to_modify)
                player_exists = True
            except Exception as e:
                if steamid_to_modify is False:
                    message = "Could not find a player to match entityid {}!".format(entityid_to_modify)
                    response_messages.add_message(message, False)
                else:
                    message = "could not find a player with steamid {}".format(steamid_to_modify)
                    response_messages.add_message(message, False)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])

            group_exists = False
            group = str(p.group("group_name"))
            if group in bot.permission_levels_list:
                group_exists = True
            else:
                message = "the group {} does not exist!".format(group)
                response_messages.add_message(message, False)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])

            if player_exists and group_exists:
                player_object_to_modify.remove_permission_level(group)
                message = "{} has been removed from the group {}".format(player_object_to_modify.name, group)
                response_messages.add_message(message, True)
                bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
                bot.socketio.emit('refresh_permissions', {"steamid": player_object_to_modify.steamid, "entityid": player_object_to_modify.entityid}, namespace='/chrani-bot/public')
                bot.players.upsert(player_object_to_modify, save=True)

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
        "usage": "/remove player <steamid/entityid> from group <group name>"
    },
    "action": remove_player_from_permission_group,
    "env": "(self, command)",
    "group": "authentication",
    "essential": False
})
