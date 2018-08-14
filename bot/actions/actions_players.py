from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
from bot.objects.player import Player
import re
import common


def on_enter_gameworld(bot, source_player, target_player, command):
    response_messages = ResponseMessage()
    try:
        target_player.is_online = True
        bot.players.upsert(target_player, save=True)
        message = "stored player-record for player {}".format(target_player.steamid)
        response_messages.add_message(message, True)
    except:
        message = "failed to player-record for player {}".format(target_player.steamid)
        response_messages.add_message(message, False)

    return response_messages


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "EnterMultiplayer",
        "usage": None
    },
    "action": on_enter_gameworld,
    "env": "(self)",
    "group": "players",
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
    "group": "players",
    "essential": True
})


def on_player_leave(bot, source_player, target_player, command):
    target_player.is_online = False
    bot.players.upsert(target_player, save=True)
    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "left the game",
        "usage": None
    },
    "action": on_player_leave,
    "env": "(self)",
    "group": "players",
    "essential": True
})


def teleport_player_to_coords(bot, source_player, target_player, command):
    p = re.search(r"send\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sto\s\((?P<coords>.*)\)", command)
    if p:
        steamid_to_teleport = p.group("steamid")
        entityid_to_teleport = p.group("entityid")
        coords_to_teleport_to = p.group("coords")
        coord_tuple = tuple(item for item in coords_to_teleport_to.split(',') if item.strip())

        if steamid_to_teleport is None:
            steamid_to_teleport = bot.players.entityid_to_steamid(entityid_to_teleport)
            if steamid_to_teleport is False:
                bot.tn.send_message_to_player(target_player, "could not find player", color=bot.chat_colors['error'])
                return False
        else:
            player_object_to_teleport = bot.players.get_by_steamid(steamid_to_teleport)
    else:
        bot.tn.send_message_to_player(target_player, "you did not specify a player. Use {}".format(common.find_action_help("players", "send player")), color=bot.chat_colors['warning'])
        return False

    return bot.tn.teleportplayer(player_object_to_teleport, coord_tuple=coord_tuple)


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "send player",
        "usage": "/send player <steamid/entityid> to <coords>"
    },
    "action": teleport_player_to_coords,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def teleport_self_to_player(bot, source_player, target_player, command):
    try:
        p = re.search(r"goto\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))", command)
        if p:
            steamid_to_teleport_to = p.group("steamid")
            entityid_to_teleport_to = p.group("entityid")
            if steamid_to_teleport_to is None:
                steamid_to_teleport_to = bot.players.entityid_to_steamid(entityid_to_teleport_to)
                if steamid_to_teleport_to is False:
                    bot.tn.send_message_to_player(target_player, "could not find player", color=bot.chat_colors['error'])
                    return False
            if int(steamid_to_teleport_to) == int(target_player.steamid):
                bot.tn.send_message_to_player(target_player, "Try meditation, if you want to find yourself ^^", color=bot.chat_colors['warning'])
                return False
            else:
                player_object_to_teleport_to = bot.players.get_by_steamid(steamid_to_teleport_to)
        else:
            bot.tn.send_message_to_player(target_player, "you did not specify a player. Use {}".format(common.find_action_help("players", "goto player")), color=bot.chat_colors['warning'])
            return False

    except Exception as e:
        logger.exception(e)
        raise KeyError

    coord_tuple = (player_object_to_teleport_to.pos_x, player_object_to_teleport_to.pos_y, player_object_to_teleport_to.pos_z)
    if bot.tn.teleportplayer(target_player, coord_tuple=coord_tuple):
        bot.tn.send_message_to_player(target_player, "You have been ported to {}'s last known location".format(player_object_to_teleport_to.name), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "Teleporting to player {} failed :(".format(player_object_to_teleport_to.name), color=bot.chat_colors['error'])
    return True


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "goto player",
        "usage": "/goto player <steamid/entityid>"
    },
    "action": teleport_self_to_player,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def teleport_player_to_self(bot, source_player, target_player, command):
    try:
        p = re.search(r"summon\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
        if p:
            steamid_to_fetch = p.group("steamid")
            entityid_to_fetch = p.group("entityid")
            if steamid_to_fetch is None:
                steamid_to_fetch = bot.players.entityid_to_steamid(entityid_to_fetch)
                if steamid_to_fetch is False:
                    bot.tn.send_message_to_player(target_player, "could not find player", color=bot.chat_colors['error'])
                    return False
            if int(steamid_to_fetch) == int(target_player.steamid):
                bot.tn.send_message_to_player(target_player, "Hands off those drugs man. They ain't good for you!", color=bot.chat_colors['warning'])
                return False
            else:
                player_object_to_teleport_to = bot.players.get_by_steamid(steamid_to_fetch)
        else:
            bot.tn.send_message_to_player(target_player, "you did not specify a player. Use {}".format(common.find_action_help("players", "summon player")), color=bot.chat_colors['warning'])
            return False

    except Exception as e:
        logger.exception(e)
        raise KeyError

    coord_tuple = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
    if bot.tn.teleportplayer(player_object_to_teleport_to, coord_tuple=coord_tuple):
        bot.tn.send_message_to_player(player_object_to_teleport_to, "You have been summoned to {}'s location".format(target_player.name), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "Summoning player {} failed :(".format(player_object_to_teleport_to.name), color=bot.chat_colors['error'])
    return True


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "summon player",
        "usage": "/summon player <steamid/entityid>"
    },
    "action": teleport_player_to_self,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def list_online_players(bot, source_player, target_player, command):
    """Lists all currently online players

    Keyword arguments:
    self -- the bot

    expected bot command:
    /online players

    example:
    /online players

    notes:
    Will list players and show their entityId
    """
    try:
        players_to_list = bot.players.get_all_players(get_online_only=True)

        for player_object_to_list in players_to_list:
            bot.tn.send_message_to_player(target_player, "{} ([ffffff]{}[-]) / authenticated: [ffffff]{}[-]".format(player_object_to_list.name, player_object_to_list.entityid, str(player_object_to_list.authenticated)), color=bot.chat_colors['success'])

    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "online players",
        "usage": "/online players"
    },
    "action": list_online_players,
    "env": "(self)",
    "group": "players",
    "essential": True
})


def list_available_player_actions(bot, source_player, target_player, command):
    """Lists all available actions and their usage for the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /list actions

    example:
    /list actions

    notes:
    It will only show the commands the player has access to.
    """
    available_player_actions = []
    if bot.actions_list is not None:
        for player_action in bot.actions_list:
            function_category = player_action["group"]
            function_name = getattr(player_action["action"], 'func_name')
            action_string = player_action["command"]["usage"]
            has_permission = bot.permissions.player_has_permission(target_player, function_name, function_category)
            if isinstance(has_permission, bool) and has_permission is True and action_string is not None:
                available_player_actions.append("({}) - [ffffff]{}[-]".format(function_category, action_string))

        bot.tn.send_message_to_player(target_player, "The following actions are available to you:", color=bot.chat_colors['success'])
        # available_player_actions = list(set(available_player_actions))

        for player_action in available_player_actions:
            bot.tn.send_message_to_player(target_player, "{}".format(player_action), color=bot.chat_colors['success'])

    return False


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "list actions",
        "usage": "/list actions"
    },
    "action": list_available_player_actions,
    "env": "(self)",
    "group": "players",
    "essential": True
})


def obliterate_player(bot, source_player, target_player, command):
    """Kicks the player and removes all bot-accessible data for the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /obliterate player <steamid/entityid>

    example:
    /obliterate player <steamid/entityid>

    notes:
    it will delete all locations and all playerdata plus the whitelist entry.
    """
    response_messages = ResponseMessage()
    p = re.search(r"obliterate\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))", command)
    if p:
        steamid_to_obliterate = p.group("steamid")
        entityid_to_obliterate = p.group("entityid")
        if steamid_to_obliterate is None:
            steamid_to_obliterate = bot.players.entityid_to_steamid(entityid_to_obliterate)
            if steamid_to_obliterate is False:
                raise KeyError

        if target_player.is_responsive() and bot.tn.kick(target_player, "Time to be born again!!"):
            response_messages.add_message("player {} has been kicked, soon to be obliterated".format(target_player.name), True)
        else:
            response_messages.add_message("player {} has not been kicked :(".format(target_player.name), False)

        location_objects_dict = bot.locations.get(target_player.steamid)
        locations_to_remove = []
        for name, location_object in location_objects_dict.iteritems():
            locations_to_remove.append(location_object)

        response_messages.add_message("found {} locations for player {}".format(len(locations_to_remove), target_player.name), True)

        for location_object in locations_to_remove:
            if bot.locations.remove(target_player.steamid, location_object.identifier):
                response_messages.add_message("locations {} has been removed".format(location_object.name), True)
            else:
                response_messages.add_message("failed to remove location {}".format(location_object.name), False)

        if bot.whitelist.player_is_on_whitelist(target_player):
            if bot.whitelist.remove(target_player):
                response_messages.add_message("player {} has been removed from the whitlist".format(target_player.name), True)
            else:
                response_messages.add_message("could not remove player {} from the whitelist :(".format(target_player.name), False)

        if bot.players.remove(target_player):
            response_messages.add_message("player {} has been removed!".format(target_player.name), True)
        else:
            response_messages.add_message("could not remove player {}".format(target_player.name), False)

        bot.webinterface.socketio.emit('remove_player_table_row', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/test')
        return response_messages
    else:
        raise ValueError("action does not fully match the trigger-string")


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "obliterate player",
        "usage": "/obliterate player <steamid/entityid>"
    },
    "action": obliterate_player,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def obliterate_me(bot, source_player, target_player, command):
    """Kicks the player and removes all bot-accessible datafor the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /obliterate me

    example:
    /obliterate me

    notes:
    it will delete all locations and all playerdata plus the whitelist entry. Currently it does NOT remove references,
    like if the player is inside a location while obliterated, the location file will not be purged. YET.
    """
    try:
        obliterate_player(bot, source_player, target_player, "obliterate player {}".format(target_player.steamid))
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "obliterate me",
        "usage": "/obliterate me"
    },
    "action": obliterate_me,
    "env": "(self)",
    "group": "players",
    "essential": False
})


def ban_player(bot, source_player, target_player, command):
    """Bans a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /ban player <steamid/entityid> for <ban_reason>

    example:
    /ban player 76561198040658370 for Being an asshat

    notes:
    both the ban-er and the ban-ee will be mentioned in the ban-message
    there is no timeframe, bans are permanent for now
    """
    try:
        p = re.search(r"ban\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sfor\s(?P<ban_reason>.+)", command)
        if p:
            steamid_to_ban = p.group("steamid")
            entityid_to_ban = p.group("entityid")
            if steamid_to_ban is None:
                steamid_to_ban = bot.players.entityid_to_steamid(entityid_to_ban)
                if steamid_to_ban is False:
                    raise KeyError

            reason_for_ban = p.group("ban_reason")
            try:
                player_object_to_ban = bot.players.get_by_steamid(steamid_to_ban)
            except KeyError:
                player_dict = {'steamid': steamid_to_ban, "name": 'unknown offline player'}
                player_object_to_ban = Player(**player_dict)

            if bot.tn.ban(player_object_to_ban, "{} banned {} for {}".format(target_player.name, player_object_to_ban.name, reason_for_ban)):
                bot.tn.send_message_to_player(player_object_to_ban, "you have been banned by {}".format(target_player.name), color=bot.chat_colors['alert'])
                bot.tn.send_message_to_player(target_player, "you have banned player {}".format(player_object_to_ban.name), color=bot.chat_colors['success'])
                bot.tn.say("{} has been banned by {} for '{}'!".format(player_object_to_ban.name, target_player.name, reason_for_ban), color=bot.chat_colors['success'])
            else:
                bot.tn.send_message_to_player(target_player, "could not find a player with id {}".format(steamid_to_ban), color=bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "ban player",
        "usage": "/ban player <steamid/entityid> for <reason>"
    },
    "action": ban_player,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def unban_player(bot, source_player, target_player, command):
    """Unbans a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /unban player <steamid/entityid>

    example:
    /unban player 76561198040658370
    """
    try:
        p = re.search(r"unban\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
        if p:
            steamid_to_unban = p.group("steamid")
            entityid_to_unban = p.group("entityid")
            if steamid_to_unban is None:
                steamid_to_unban = bot.players.entityid_to_steamid(entityid_to_unban)

            player_object_to_unban = bot.players.load(steamid_to_unban)

            if bot.tn.unban(player_object_to_unban):
                bot.tn.send_message_to_player(target_player, "you have unbanned player {}".format(player_object_to_unban.name), color=bot.chat_colors['success'])
                bot.tn.say("{} has been unbanned by {}.".format(player_object_to_unban.name, target_player.name), color=bot.chat_colors['success'])
                return True

            bot.tn.send_message_to_player(target_player, "could not find a player with steamid {}".format(steamid_to_unban), color=bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "unban player",
        "usage": "/unban player <steamid/entityid>"
    },
    "action": unban_player,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})


def kick_player(bot, source_player, target_player, command):
    """Kicks a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /kick player <steamid/entityid> for <kick_reason>

    example:
    /kick player 76561198040658370 for Stinking up the room!
    """
    try:
        p = re.search(r"kick\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sfor\s(?P<kick_reason>.+)", command)
        if p:
            steamid_to_kick = p.group("steamid")
            entityid_to_kick = p.group("entityid")
            if steamid_to_kick is None:
                steamid_to_kick = bot.players.entityid_to_steamid(entityid_to_kick)

            reason_for_kick = p.group("kick_reason")
            try:
                player_object_to_kick = bot.players.get_by_steamid(steamid_to_kick)
            except KeyError:
                bot.tn.send_message_to_player(target_player, "could not find a player with id {}".format(steamid_to_kick), color=bot.chat_colors['warning'])
                return

            if bot.tn.kick(player_object_to_kick, reason_for_kick):
                bot.tn.send_message_to_player(target_player, "you have kicked {}".format(player_object_to_kick.name), color=bot.chat_colors['success'])
                bot.tn.say("{} has been kicked by {} for '{}'!".format(player_object_to_kick.name, target_player.name, reason_for_kick), color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "kick player",
        "usage": "/kick player <steamid/entityid> for <reason>"
    },
    "action": kick_player,
    "env": "(self, command)",
    "group": "players",
    "essential": False
})
