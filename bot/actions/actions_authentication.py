import re
from bot.modules.logger import logger
import common


def on_player_join(bot, source_player, target_player, command):
    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "joined the game",
        "usage": None
    },
    "action": on_player_join,
    "env": "(self)",
    "group": "authentication",
    "essential": True
})


def on_player_leave(bot, source_player, target_player, command):
    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "left the game",
        "usage": None
    },
    "action": on_player_leave,
    "env": "(self)",
    "group": "authentication",
    "essential": True
})


def on_enter_gameworld(bot, source_player, target_player, command):
    """Will greet an unauthenticated player

    Keyword arguments:
    self -- the bot

    notes:
    does nothing for authenticated players
    """
    if target_player.has_permission_level("authenticated") is not True:
        bot.tn.send_message_to_player(target_player, "read the rules on https://chrani.net/chrani-bot", color=bot.chat_colors['warning'])
        bot.tn.send_message_to_player(target_player, "this is a development server. you can play here, but there's no support or anything really.", color=bot.chat_colors['info'])
        bot.tn.send_message_to_player(target_player, "Enjoy!", color=bot.chat_colors['info'])

    if target_player.initialized is not True:
        target_player.initialized = True
        bot.players.upsert(target_player)


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "EnterMultiplayer",
        "usage": None
    },
    "action": on_enter_gameworld,
    "env": "(self)",
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
    "env": "(self)",
    "group": "authentication",
    "essential": True
})


def password(bot, source_player, target_player, command):
    """Adds player to permission-group(s) according to the password entered

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
    p = re.search(r"password\s(?P<password>\w+)$", command)
    try:
        pwd = p.group("password")
    except (AttributeError, IndexError) as e:
        bot.tn.send_message_to_player(target_player, "You have entered no password. Use {}".format(common.find_action_help("authentication", "password")), color=bot.chat_colors['warning'])
        return False

    if pwd not in bot.passwords.values() and target_player.authenticated is not True :
        bot.tn.send_message_to_player(target_player, "You have entered a wrong password!", color=bot.chat_colors['warning'])
        return False
    elif pwd not in bot.passwords.values() and target_player.authenticated is True:
        target_player.set_authenticated(False)
        target_player.remove_permission_level("authenticated")
        bot.tn.send_message_to_player(target_player, "You have lost your authentication!", color=bot.chat_colors['warning'])

        bot.players.upsert(target_player, save=True)
        return False

    if target_player.authenticated is not True:
        target_player.set_authenticated(True)
        target_player.add_permission_level("authenticated")
        bot.tn.say("{} joined the ranks of literate people. Welcome!".format(target_player.name), color=bot.chat_colors['background'])

    """ makeshift promotion system """
    # TODO: well, this action should only care about general authentication. things like admin and mod should be handled somewhere else really
    if pwd == bot.passwords['admin']:
        target_player.add_permission_level("admin")
        bot.tn.send_message_to_player(target_player, "you are an Admin", color=bot.chat_colors['success'])
    elif pwd == bot.passwords['mod']:
        target_player.add_permission_level("mod")
        bot.tn.send_message_to_player(target_player, "you are a Moderator", color=bot.chat_colors['success'])
    elif pwd == bot.passwords['donator']:
        target_player.add_permission_level("donator")
        bot.tn.send_message_to_player(target_player, "you are a Donator. Thank you <3", color=bot.chat_colors['success'])

    bot.players.upsert(target_player, save=True)
    return True


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "password",
        "usage": "/password <password>"
    },
    "action": password,
    "env": "(self, command)",
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
    p = re.search(r"add\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sto\sgroup\s(?P<group_name>\w+)$", command)
    if p:
        steamid_to_modify = p.group("steamid")
        entityid_to_modify = p.group("entityid")
        if steamid_to_modify is None:
            steamid_to_modify = bot.players.entityid_to_steamid(entityid_to_modify)
            if steamid_to_modify is False:
                raise KeyError

        group = str(p.group("group_name"))
        if group not in bot.permission_levels_list:
            bot.tn.send_message_to_player(target_player, "the group {} does not exist!".format(group), color=bot.chat_colors['success'])
            return False

        try:
            player_object_to_modify = bot.players.get_by_steamid(steamid_to_modify)
            player_object_to_modify.add_permission_level(group)
            bot.tn.send_message_to_player(target_player, "{} has been added to the group {}".format(target_player.name, group), color=bot.chat_colors['success'])
        except Exception:
            bot.tn.send_message_to_player(target_player,"could not find a player with steamid {}".format(steamid_to_modify), color=bot.chat_colors['warning'])
            return

        bot.players.upsert(player_object_to_modify, save=True)


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "add player",
        "usage": "/add player <steamid/entityid> to group <group name>"
    },
    "action": add_player_to_permission_group,
    "env": "(self, command)",
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
    p = re.search(r"remove\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfrom\sgroup\s(?P<group_name>\w+)$", command)
    if p:
        steamid_to_modify = p.group("steamid")
        entityid_to_modify = p.group("entityid")
        if steamid_to_modify is None:
            steamid_to_modify = bot.players.entityid_to_steamid(entityid_to_modify)
            if steamid_to_modify is False:
                raise KeyError

        group = str(p.group("group_name"))
        if group not in bot.permission_levels_list:
            bot.tn.send_message_to_player(target_player, "the group {} does not exist!".format(group), color=bot.chat_colors['success'])
            return False

        try:
            player_object_to_modify = bot.players.get_by_steamid(steamid_to_modify)
            player_object_to_modify.remove_permission_level(group)
            bot.tn.send_message_to_player(target_player, "{} has been removed from the group {}".format(target_player.name, group), color=bot.chat_colors['success'])
        except Exception:
            bot.tn.send_message_to_player(target_player,"could not find a player with steamid {}".format(steamid_to_modify), color=bot.chat_colors['warning'])
            return

        bot.players.upsert(player_object_to_modify, save=True)


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
