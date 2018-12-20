import re
from bot.objects.location import Location
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common


def password(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        lobby_exists = False
        try:
            location_object = chrani_bot.locations.get('system', "lobby")
            lobby_exists = True
        except KeyError:
            response_messages.add_message("no lobby found", False)

        if lobby_exists is False:
            return response_messages

        p = re.search(r"password\s(\w+)$", command)
        if p:
            pwd = p.group(1)
            if pwd in chrani_bot.passwords.values():
                spawn_exists = False
                try:
                    location_object = chrani_bot.locations.get(target_player.steamid, 'spawn')
                    spawn_exists = True
                except KeyError:
                    response_messages.add_message("no spawn found", True)

                # if the spawn is enabled, do port the player and disable it.
                if spawn_exists and location_object.enabled and chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, location_object=location_object):
                    message = "You have been ported back to your original spawn!"
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
                    response_messages.add_message(message, True)
                    location_object.enabled = False
                    chrani_bot.locations.upsert(location_object, save=True)
                else:
                    message = "Taking you to your original spawn failed oO!"
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])
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
        "trigger": "password",
        "usage": "/password <password>"
    },
    "action": password,
    "group": "lobby",
    "essential": True
})


def set_up_lobby(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        location_object = Location()
        location_object.set_owner('system')
        name = 'The Lobby'

        location_object.set_name(name)
        location_object.radius = float(chrani_bot.settings.get_setting_by_name(name="location_default_radius"))
        location_object.warning_boundary = float(chrani_bot.settings.get_setting_by_name(name="location_default_warning_boundary"))

        location_object.set_coordinates(target_player)
        location_object.set_identifier('lobby')
        location_object.set_description('The \"there is no escape\" Lobby')
        location_object.set_shape("sphere")

        messages_dict = location_object.get_messages_dict()
        messages_dict["entered_locations_core"] = "authenticate with {} to leave the lobby".format(
            common.find_action_help("authentication", "password"))
        messages_dict["left_locations_core"] = "You are about to leave the lobby area!"
        messages_dict["entered_location"] = "You have entered the lobby"
        messages_dict["left_location"] = "You have left the lobby"
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([target_player.steamid])

        chrani_bot.locations.upsert(location_object, save=True)

        message = "You have set up a lobby"
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        response_messages.add_message(message, True)
        chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Set up the perimeter with {}, while standing on the edge of it.".format(
            common.find_action_help("lobby", "edit lobby outer perimeter")), chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "add lobby",
        "usage": "/add lobby"
    },
    "action": set_up_lobby,
    "group": "lobby",
    "essential": False
})


def set_up_lobby_outer_perimeter(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            location_object = chrani_bot.locations.get('system', 'lobby')
        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You need to set up a lobby first silly: {}".format(
                common.find_action_help("lobby", "set_up_lobby")), chrani_bot.chat_colors['warning'])
            return False

        coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
        distance_to_location = location_object.get_distance(coords)
        set_radius, allowed_range = location_object.set_radius(distance_to_location)
        if set_radius is True:
            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            message = "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
            response_messages.add_message(message, True)
        else:
            message = "Your given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])
            response_messages.add_message(message, False)

        if set_radius and location_object.radius <= location_object.warning_boundary:
            set_boundary, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
            if set_boundary is True:
                message = "The inner core has been set to match the outer perimeter."
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])
                response_messages.add_message(message, True)

        chrani_bot.locations.upsert(location_object, save=True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby outer perimeter",
        "usage": "/edit lobby outer perimeter"
    },
    "action": set_up_lobby_outer_perimeter,
    "group": "lobby",
    "essential": False
})


def set_up_lobby_inner_perimeter(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        try:
            location_object = chrani_bot.locations.get('system', 'lobby')
        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You need to set up a lobby first silly: {}".format(
                common.find_action_help("lobby", "set_up_lobby")), chrani_bot.chat_colors['warning'])
            return False

        coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
        distance_to_location = location_object.get_distance(coords)
        set_boundary, allowed_range = location_object.set_warning_boundary(distance_to_location)
        if set_boundary is True:
            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            message = "The lobby warning perimeter ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
            response_messages.add_message(message, True)
        else:
            message = "Your given range ({}) seems to be invalid ^^".format(int(location_object.warning_boundary * 2))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])
            response_messages.add_message(message, False)

        chrani_bot.locations.upsert(location_object, save=True)
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby inner perimeter",
        "usage": "/edit lobby inner perimeter"
    },
    "action": set_up_lobby_inner_perimeter,
    "group": "lobby",
    "essential": False
})


def goto_lobby(chrani_bot, source_player, target_player, command):
    try:
        try:
            location_object = chrani_bot.locations.get('system', 'lobby')
            if chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, location_object=location_object):
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You have ported to the lobby", chrani_bot.chat_colors['standard'])
        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "There is no lobby :(", chrani_bot.chat_colors['warning'])

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "goto lobby",
        "usage": "/goto lobby"
    },
    "action": goto_lobby,
    "group": "lobby",
    "essential": False
})


def remove_lobby(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        try:
            location_object = chrani_bot.locations.get("system", "lobby")
            chrani_bot.locations.remove(location_object)
            message = "lobby has been removed oO"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
            chrani_bot.socketio.emit('remove_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        except KeyError:
            message = "no lobby found oO"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "remove lobby",
        "usage": "/remove lobby"
    },
    "action": remove_lobby,
    "group": "lobby",
    "essential": False
})


def set_up_lobby_teleport(chrani_bot, source_player, target_player, command):
    try:
        try:
            location_object = chrani_bot.locations.get('system', 'lobby')
        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "coming from the wrong end... set up the lobby first!", chrani_bot.chat_colors['warning'])
            return False

        if location_object.set_teleport_coordinates(target_player):
            chrani_bot.locations.upsert(location_object, save=True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the teleport for {} has been set up!".format('lobby'), chrani_bot.chat_colors['success'])
        else:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your position seems to be outside of the location", chrani_bot.chat_colors['warning'])

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby teleport",
        "usage": "/edit lobby teleport"
    },
    "action": set_up_lobby_teleport,
    "group": "lobby",
    "essential": False
})
