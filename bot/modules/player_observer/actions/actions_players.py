from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
from bot.objects.player import Player
import re
import common


def on_enter_telnet(chrani_bot, source_player, target_player, command):
    """Will greet an unauthenticated player

    Keyword arguments:
    self -- the bot

    notes:
    does nothing for authenticated players
    """
    try:
        response_messages = ResponseMessage()
        response_messages.add_message("Player {} has been seen in the stream".format(target_player.name), True)

        chrani_bot.socketio.emit('update_player_table_row', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "found in the stream",
        "usage": None
    },
    "action": on_enter_telnet,
    "group": "players",
    "essential": True
})


def on_enter_gameworld(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            chrani_bot.players.upsert(target_player, save=True)
            message = "stored player-record for player {}".format(target_player.steamid)
            chrani_bot.socketio.emit('update_player_table_row', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
            response_messages.add_message(message, True)
        except:
            message = "failed to store player-record for player {}".format(target_player.steamid)
            response_messages.add_message(message, False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "found in the world",
        "usage": None
    },
    "action": on_enter_gameworld,
    "group": "players",
    "essential": True
})


def on_player_leave(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        chrani_bot.players.upsert(target_player, save=True)
        chrani_bot.socketio.emit('update_player_table_row', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
        message = "Player {} left the game".format(target_player.name)
        response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "left the game",
        "usage": None
    },
    "action": on_player_leave,
    "group": "players",
    "essential": True
})


def on_player_death(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        target_player.is_initialized = False
        chrani_bot.players.upsert(target_player, save=True)
        message="player {} died".format(target_player.name)
        response_messages.add_message(message, False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "on player death",
        "usage": None
    },
    "action": on_player_death,
    "group": "players",
    "essential": True
})


def on_player_kill(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        target_player.is_initialized = False
        chrani_bot.players.upsert(target_player, save=True)
        message="player {} got killed :/".format(target_player.name)
        response_messages.add_message(message, False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "on player killed",
        "usage": None
    },
    "action": on_player_kill,
    "group": "players",
    "essential": True
})


def teleport_player_to_coords(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"send\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sto\s\((?P<coords>.*)\)", command)
        if p:
            steamid_to_teleport = p.group("steamid")
            entityid_to_teleport = p.group("entityid")
            coords_to_teleport_to = p.group("coords")
            if coords_to_teleport_to is None:
                coords_are_valid = False
            else:
                coords_are_valid = True

            if steamid_to_teleport is None:
                steamid_to_teleport = chrani_bot.players.entityid_to_steamid(entityid_to_teleport)
                if steamid_to_teleport is False:
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "could not find player", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))
                    return False
            else:
                player_object_to_teleport = chrani_bot.players.get_by_steamid(steamid_to_teleport)
        else:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "you did not specify a player. Use {}".format(
                common.find_action_help("players", "send player")), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
            return False

        coord_tuple = tuple(item for item in coords_to_teleport_to.split(',') if item.strip())
        if coords_are_valid and chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_object_to_teleport, coord_tuple=coord_tuple):
            response_messages.add_message("player {} got teleported to {}".format(player_object_to_teleport.name, coord_tuple), True)
        else:
            response_messages.add_message("teleporting player {} failed".format(player_object_to_teleport.name), False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "send player",
        "usage": "/send player <steamid/entityid> to <coords>"
    },
    "action": teleport_player_to_coords,
    "group": "players",
    "essential": False
})


def teleport_self_to_player(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            p = re.search(r"goto\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))", command)
            if p:
                steamid_to_teleport_to = p.group("steamid")
                entityid_to_teleport_to = p.group("entityid")
                if steamid_to_teleport_to is None:
                    steamid_to_teleport_to = chrani_bot.players.entityid_to_steamid(entityid_to_teleport_to)
                    if steamid_to_teleport_to is False:
                        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "could not find player", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))
                        return False
                if int(steamid_to_teleport_to) == int(target_player.steamid):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "Try meditation, if you want to find yourself ^^", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                    return False
                else:
                    player_object_to_teleport_to = chrani_bot.players.get_by_steamid(steamid_to_teleport_to)
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "you did not specify a player. Use {}".format(
                    common.find_action_help("players", "goto player")), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

        except Exception as e:
            logger.debug(e)
            raise KeyError

        coord_tuple = player_object_to_teleport_to.get_coord_tuple()
        if chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, coord_tuple=coord_tuple):
            message = "You have been ported to {}'s last known location".format(player_object_to_teleport_to.name)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            response_messages.add_message(message, True)
        else:
            message = "Teleporting to player {} failed :(".format(player_object_to_teleport_to.name)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))
            response_messages.add_message(message, False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "goto player",
        "usage": "/goto player <steamid/entityid>"
    },
    "action": teleport_self_to_player,
    "group": "players",
    "essential": False
})


def teleport_player_to_self(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            p = re.search(r"summon\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
            if p:
                steamid_to_fetch = p.group("steamid")
                entityid_to_fetch = p.group("entityid")
                if steamid_to_fetch is None:
                    steamid_to_fetch = chrani_bot.players.entityid_to_steamid(entityid_to_fetch)
                    if steamid_to_fetch is False:
                        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "could not find player", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))
                        return False
                if int(steamid_to_fetch) == int(target_player.steamid):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "Hands off those drugs man. They ain't good for you!", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                    return False
                else:
                    player_object_to_teleport_to = chrani_bot.players.get_by_steamid(steamid_to_fetch)
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, "you did not specify a player. Use {}".format(
                    common.find_action_help("players", "summon player")), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

        except Exception as e:
            logger.debug(e)
            raise KeyError

        coord_tuple = target_player.get_coord_tuple()
        if chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_object_to_teleport_to, coord_tuple=coord_tuple):
            message = "You have been summoned to {}'s location".format(target_player.name)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            response_messages.add_message(message, True)
        else:
            message = "Summoning player {} failed :(".format(player_object_to_teleport_to.name)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm",target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))
            response_messages.add_message(message, False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "summon player",
        "usage": "/summon player <steamid/entityid>"
    },
    "action": teleport_player_to_self,
    "group": "players",
    "essential": False
})


def list_online_players(chrani_bot, source_player, target_player, command):
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
        response_messages = ResponseMessage()
        try:
            players_to_list = chrani_bot.players.get_all_players(get_online_only=True)

            for player_object_to_list in players_to_list:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "{} ([ffffff]{}[-]) / authenticated: [ffffff]{}[-]".format(player_object_to_list.name, player_object_to_list.entityid, str(player_object_to_list.authenticated)), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))

            message = "Listed {} online players.".format(len(players_to_list))
            response_messages.add_message(message, True)

        except Exception as e:
            logger.debug(e)
            pass

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "online players",
        "usage": "/online players"
    },
    "action": list_online_players,
    "group": "players",
    "essential": True
})


def list_available_player_actions(chrani_bot, source_player, target_player, command):
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
    try:
        response_messages = ResponseMessage()
        available_player_actions = []
        if chrani_bot.actions_list is not None:
            for player_action in chrani_bot.player_observer.actions_list:
                function_category = player_action["group"]
                function_name = getattr(player_action["action"], 'func_name')
                action_string = player_action["command"]["usage"]
                has_permission = chrani_bot.permissions.player_has_permission(target_player, function_name, function_category)
                if isinstance(has_permission, bool) and has_permission is True and action_string is not None:
                    available_player_actions.append("({}) - [ffffff]{}[-]".format(function_category, action_string))

            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "The following actions are available to you:", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            # available_player_actions = list(set(available_player_actions))  # this removes entries present in more than one group

            for player_action in available_player_actions:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "{}".format(player_action), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))

            message = "Listed {} available actions.".format(len(available_player_actions))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message)
            response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "list actions",
        "usage": "/list actions"
    },
    "action": list_available_player_actions,
    "group": "players",
    "essential": True
})


def obliterate_player(chrani_bot, source_player, target_player, command):
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
    try:
        response_messages = ResponseMessage()
        p = re.search(r"obliterate\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))", command)
        if p:
            steamid_to_obliterate = p.group("steamid")
            entityid_to_obliterate = p.group("entityid")
            if steamid_to_obliterate is None:
                steamid_to_obliterate = chrani_bot.players.entityid_to_steamid(entityid_to_obliterate)
                if steamid_to_obliterate is False:
                    raise KeyError

            reason_for_kick = "Your profile and all your bot stuff will be removed now!"
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "ban", target_player, reason_for_kick)

            try:
                location_objects_dict = chrani_bot.locations.get(target_player.steamid)
            except KeyError:
                location_objects_dict = {}

            locations_to_remove = []
            for name, location_object in location_objects_dict.iteritems():
                locations_to_remove.append(location_object)

            response_messages.add_message("found {} locations for player {}".format(len(locations_to_remove), target_player.name), True)

            for location_object in locations_to_remove:
                if chrani_bot.locations.remove(target_player.steamid, location_object.identifier):
                    response_messages.add_message("locations {} has been removed".format(location_object.name), True)
                else:
                    response_messages.add_message("failed to remove location {}".format(location_object.name), False)

            if chrani_bot.whitelist.player_is_on_whitelist(target_player.steamid):
                if chrani_bot.whitelist.remove(target_player):
                    response_messages.add_message("player {} has been removed from the whitlist".format(target_player.name), True)
                else:
                    response_messages.add_message("could not remove player {} from the whitelist :(".format(target_player.name), False)

            chrani_bot.dom["bot_data"]["player_data"][target_player.steamid]["is_to_be_obliterated"] = True
            response_messages.add_message("player {} is marked for removal ^^".format(target_player.name), True)

            target_player.is_online = False
            response_messages.add_message("player {} is set to offlilne ^^".format(target_player.name), True)
            # target_player.update()

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "obliterate player",
        "usage": "/obliterate player <steamid/entityid>"
    },
    "action": obliterate_player,
    "group": "players",
    "essential": False
})


def obliterate_me(chrani_bot, source_player, target_player, command):
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
        return obliterate_player(chrani_bot, source_player, target_player, "obliterate player {}".format(target_player.steamid))

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "obliterate me",
        "usage": "/obliterate me"
    },
    "action": obliterate_me,
    "group": "players",
    "essential": False
})


def ban_player(chrani_bot, source_player, target_player, command):
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
        response_messages = ResponseMessage()
        p = re.search(r"ban\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sfor\s(?P<ban_reason>.+)", command)
        if p:
            steamid_to_ban = p.group("steamid")
            entityid_to_ban = p.group("entityid")
            if steamid_to_ban is None:
                steamid_to_ban = chrani_bot.players.entityid_to_steamid(entityid_to_ban)
                if steamid_to_ban is False:
                    raise KeyError

            reason_for_ban = p.group("ban_reason")
            try:
                player_object_to_ban = chrani_bot.players.get_by_steamid(steamid_to_ban)
            except KeyError:
                player_dict = {'steamid': steamid_to_ban, "name": 'unknown offline player'}
                player_object_to_ban = Player(**player_dict)

            if not player_object_to_ban.is_banned and chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "ban", player_object_to_ban, reason_for_ban, 24 * 365):
                player_object_to_ban.is_banned = True
                chrani_bot.socketio.emit('refresh_player_actions', {"steamid": player_object_to_ban.steamid, "entityid": player_object_to_ban.entityid}, namespace='/chrani-bot/public')
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object_to_ban, "you have been banned by {}".format(source_player.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "you have banned player {}".format(player_object_to_ban.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                message = "{} has been banned by {} for '{}'!".format(player_object_to_ban.name, source_player.name, reason_for_ban)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                response_messages.add_message(message, True)
                chrani_bot.players.upsert(player_object_to_ban, save=True)
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "could not find a player with id {}".format(steamid_to_ban), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "ban player",
        "usage": "/ban player <steamid/entityid> for <reason>"
    },
    "action": ban_player,
    "group": "players",
    "essential": False
})


def unban_player(chrani_bot, source_player, target_player, command):
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
        response_messages = ResponseMessage()
        p = re.search(r"unban\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))", command)
        if p:
            steamid_to_unban = p.group("steamid")
            entityid_to_unban = p.group("entityid")
            if steamid_to_unban is None:
                steamid_to_unban = chrani_bot.players.entityid_to_steamid(entityid_to_unban)

            player_object_to_unban = chrani_bot.players.load(steamid_to_unban)

            if chrani_bot.tn.unban(player_object_to_unban):
                player_object_to_unban.is_banned = False
                chrani_bot.socketio.emit('refresh_player_actions', {"steamid": player_object_to_unban.steamid, "entityid": player_object_to_unban.entityid}, namespace='/chrani-bot/public')
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", source_player, "you have unbanned player {}".format(player_object_to_unban.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                message = "{} has been unbanned by {}.".format(player_object_to_unban.name, source_player.name)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                response_messages.add_message(message, True)
                chrani_bot.players.upsert(player_object_to_unban, save=True)
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "could not find a player with steamid {}".format(steamid_to_unban), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "unban player",
        "usage": "/unban player <steamid/entityid>"
    },
    "action": unban_player,
    "group": "players",
    "essential": False
})


def kick_player(chrani_bot, source_player, target_player, command):
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
        response_messages = ResponseMessage()
        p = re.search(r"kick\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\sfor\s(?P<kick_reason>.+)", command)
        if p:
            steamid_to_kick = p.group("steamid")
            entityid_to_kick = p.group("entityid")
            if steamid_to_kick is None:
                steamid_to_kick = chrani_bot.players.entityid_to_steamid(entityid_to_kick)

            reason_for_kick = p.group("kick_reason")
            try:
                player_object_to_kick = chrani_bot.players.get_by_steamid(steamid_to_kick)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "could not find a player with id {}".format(steamid_to_kick), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return

            if chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "kick", player_object_to_kick, reason_for_kick):
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", source_player, "you have kicked {}".format(player_object_to_kick.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                message = "{} has been kicked by {} for '{}'!".format(player_object_to_kick.name, source_player.name, reason_for_kick)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                response_messages.add_message(message, True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "kick player",
        "usage": "/kick player <steamid/entityid> for <reason>"
    },
    "action": kick_player,
    "group": "players",
    "essential": False
})
