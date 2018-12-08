import re
from bot.objects.location import Location
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def check_building_site(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        bases_near_list, landclaims_near_list = chrani_bot.check_for_homes(target_player)

        if not bases_near_list and not landclaims_near_list:
            message = "Nothing near or far. Feel free to build here"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        else:
            message = "Bases near: {}, Landclaims near: {}".format(len(bases_near_list), len(landclaims_near_list))
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "can i build here",
        "usage": "/can i build here"
    },
    "action": check_building_site,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        bases_near_list, landclaims_near_list = chrani_bot.check_for_homes(target_player)

        can_i_build_here = False
        if not bases_near_list and not landclaims_near_list:
            can_i_build_here = True
        else:
            message = "Can not set up a home here. Other bases are too close!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['error'])

        location_object = Location()
        location_object.set_owner(target_player.steamid)
        name = 'My Home'

        location_object.set_name(name)
        location_object.radius = float(chrani_bot.settings.get_setting_by_name(name="location_default_radius"))
        location_object.warning_boundary = float(chrani_bot.settings.get_setting_by_name(name="location_default_warning_boundary"))

        location_object.set_coordinates(target_player)
        location_object.set_identifier('home')

        location_object.set_description("{}\'s home".format(target_player.name))
        location_object.set_shape("square")

        messages_dict = location_object.get_messages_dict()
        messages_dict["entered_locations_core"] = None
        messages_dict["left_locations_core"] = None
        messages_dict["entered_location"] = "you have entered {}\'s estate".format(target_player.name)
        messages_dict["left_location"] = "you have left {}\'s estate".format(target_player.name)
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([target_player.steamid])

        chrani_bot.locations.upsert(location_object, save=True)

        chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
        chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')

        message = "{} has decided to settle down!".format(target_player.name)
        response_messages.add_message(message, True)
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['standard'])
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Home is where your hat is!", chrani_bot.chat_colors['success'])

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "add home",
        "usage": "/add home"
    },
    "action": set_up_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def remove_home(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            pass

        if player_home_exists and chrani_bot.locations.remove(target_player.steamid, 'home'):
            message = "Your home has been removed!"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['standard'])

            chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
            chrani_bot.socketio.emit('remove_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        else:
            message = "I could not find your home. Did you set one up?"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "remove home",
        "usage": "/remove home"
    },
    "action": remove_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_teleport(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        if player_home_exists and location_object.set_teleport_coordinates(target_player):
            chrani_bot.locations.upsert(location_object, save=True)
            message = "your teleport has been set up!"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        else:
            message = "your position seems to be outside your home"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit home teleport",
        "usage": "/edit home teleport"
    },
    "action": set_up_home_teleport,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def protect_inner_core(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        if player_home_exists and location_object.set_protected_core(True):
            chrani_bot.locations.upsert(location_object, save=True)
            message = "your home is now protected!"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your home is now protected!", chrani_bot.chat_colors['success'])
            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        else:
            message = "something went wrong :("
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "enable home protection",
        "usage": "/enable home protection"
    },
    "action": protect_inner_core,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def unprotect_inner_core(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        if player_home_exists and location_object.set_protected_core(False):
            chrani_bot.locations.upsert(location_object, save=True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your home is now unprotected!", chrani_bot.chat_colors['success'])
            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        else:
            message = "something went wrong :("
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "disable home protection",
        "usage": "/disable home protection"
    },
    "action": unprotect_inner_core,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_name(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        description_found = False
        p = re.search(r"edit\shome\sname\s([\W\w\s]{1,19})$", command)
        if p:
            description = p.group(1)
            description_found = True

        if player_home_exists and description_found:
            location_object.set_description(description)
            messages_dict = {
                "left_locations_core": "you are leaving {}\'s core".format(description),
                "left_location": "you are leaving {}".format(description),
                "entered_location": "you are entering {}".format(description),
                "entered_locations_core": "you are entering {}\'s core".format(description)
            }
            location_object.set_messages(messages_dict)
            chrani_bot.locations.upsert(location_object, save=True)

            message = "Your home is called {} now \o/".format(location_object.description)
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['standard'])

            chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        else:
            message = "something went wrong :("
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit home name",
        "usage": "/edit home name <name>"
    },
    "action": set_up_home_name,
    "env": "(self, command)",
    "group": "home",
    "essential": False
})


def take_me_home(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            if location_object.player_is_inside_boundary(target_player):
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "eh, you already ARE home oO".format(target_player.name), chrani_bot.chat_colors['warning'])
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, location_object=location_object)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "you have ported home!".format(target_player.name), chrani_bot.chat_colors['success'])

        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You seem to be homeless".format(target_player.name), chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "take me home",
        "usage": "/take me home"
    },
    "action": take_me_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def goto_player_home(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"take\sme\sto\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\shome", command)
        if p:
            player_steamid = p.group("steamid")
            player_entityid = p.group("entityid")
            if player_steamid is None:
                player_steamid = chrani_bot.players.entityid_to_steamid(player_entityid)
                if player_steamid is False:
                    raise KeyError

            try:
                player_object_to_port_to = chrani_bot.players.load(player_steamid)
                location_object = chrani_bot.locations.get(player_object_to_port_to.steamid, "home")
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, location_object=location_object)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You went to visit {}'s home".format(player_object_to_port_to.name), chrani_bot.chat_colors['standard'])
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object_to_port_to, "{} went to visit your home!".format(target_player.name), chrani_bot.chat_colors['warning'])
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Could not find {}'s home".format(player_steamid), chrani_bot.chat_colors['warning'])
                pass

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "take me to player",
        "usage": "/take me to player <steamid/entityid> home"
    },
    "action": goto_player_home,
    "env": "(self, command)",
    "group": "home",
    "essential": False
})


def set_up_home_outer_perimeter(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        coords_are_valid = False
        if player_home_exists:
            coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
            distance_to_location = location_object.get_distance(coords)
            set_radius, allowed_range = location_object.set_radius(distance_to_location)
            if set_radius is True:
                coords_are_valid = True
            else:
                message = "you given range ({}) seems to be invalid :(".format(int(location_object.radius * 2))
                response_messages.add_message(message, False)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        if player_home_exists and coords_are_valid:
            message = "your estate ends here and spans {} meters ^^".format(int(location_object.radius * 2))
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])

            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')

            if location_object.radius <= location_object.warning_boundary:
                set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
                if set_radius is True:
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the inner core has been set to match the outer perimeter.", chrani_bot.chat_colors['warning'])

            chrani_bot.locations.upsert(location_object, save=True)
        else:
            message = "something went wrong :("
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages
    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit home outer perimeter",
        "usage": "/edit home outer perimeter"
    },
    "action": set_up_home_outer_perimeter,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_inner_perimeter(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()

        player_home_exists = False
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "home")
            player_home_exists = True
        except KeyError:
            message = "coming from the wrong end... set up a home first!"
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        coords_are_valid = False
        if player_home_exists:
            coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
            distance_to_location = location_object.get_distance(coords)
            set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location)
            if set_radius is True:
                coords_are_valid = True
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "you given range ({}) seems to be invalid. Are you inside your home area?".format(int(location_object.warning_boundary * 2)), chrani_bot.chat_colors['warning'])

        if player_home_exists and coords_are_valid:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your private area ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2)), chrani_bot.chat_colors['success'])

            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
        else:
            message = "something went wrong :("
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit home inner perimeter",
        "usage": "/edit home inner perimeter"
    },
    "action": set_up_home_inner_perimeter,
    "env": "(self)",
    "group": "home",
    "essential": False
})


