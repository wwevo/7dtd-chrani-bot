import re
from bot.objects.location import Location
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common

location_identifier_regex = r"[\w\s(\-\_\'\"\(\)\!\?)]{1,19}"


def set_up_location(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"add\slocation\s(?P<location_name>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            name = p.group("location_name")
            location_name_is_not_reserved = False
            if name in chrani_bot.settings.get_setting_by_name(name="restricted_names"):
                message = "{} is a reserved name!".format(name)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)
            else:
                location_name_is_not_reserved = True

            location_name_is_valid = False
            if len(name) >= 19:
                message = "{} is too long. Keep it shorter than 19 letters ^^".format(name)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)
            else:
                location_name_is_valid = True

            location_name_not_in_use = False
            location_object = Location()
            location_object.set_name(name)
            identifier = location_object.create_identifier(name)  # generate the identifier from the name
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
                message = "a location with the identifier {} already exists".format(identifier)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)
            except KeyError:
                location_object.set_identifier(identifier)
                location_name_not_in_use = True

            if location_name_is_valid and location_name_is_not_reserved and location_name_not_in_use:
                location_object.radius = float(chrani_bot.settings.get_setting_by_name(name="location_default_radius"))
                location_object.warning_boundary = float(chrani_bot.settings.get_setting_by_name(name="location_default_warning_boundary"))

                location_object.set_coordinates(target_player)
                location_object.set_owner(target_player.steamid)
                location_object.set_shape("square")
                location_object.protected_core_whitelist = []

                messages_dict = location_object.get_messages_dict()
                messages_dict["entered_locations_core"] = "you have entered {}s core".format(name)
                messages_dict["left_locations_core"] = "you have left {}s core".format(name)
                messages_dict["entered_location"] = "you have entered the location {}".format(name)
                messages_dict["left_location"] = "you have left the location {}".format(name)

                location_object.set_messages(messages_dict)
                chrani_bot.locations.upsert(location_object, save=True)

                response_messages.add_message("A location with the identifier {} has been created".format(identifier), True)

                chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You have created a location, it is stored as {} and spans {} meters.".format(identifier, int(location_object.radius * 2)), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "use '{}' to access it with commands like /edit location name {} = Whatever the name shall be".format(identifier, identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            else:
                response_messages.add_message("Location {} could not be created :(".format(identifier), False)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "add location",
        "usage": "/add location <location name>"
    },
    "action": set_up_location,
    "group": "locations",
    "essential": False
})


def set_up_location_teleport(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"edit\slocation\steleport\s(?P<location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "coming from the wrong end... set up the location first!", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            if location_object.set_teleport_coordinates(target_player):
                chrani_bot.locations.upsert(location_object, save=True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the teleport for {} has been set up!".format(identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your position seems to be outside the location", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit location teleport",
        "usage": "/edit location teleport <location_identifier>"
    },
    "action": set_up_location_teleport,
    "group": "locations",
    "essential": False
})


def set_up_location_name(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"edit\slocation\sname\s(?P<location_identifier>{lir})\s=\s(?P<location_name>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            name = p.group("location_name")
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
                location_object.set_name(name)
                messages_dict = location_object.get_messages_dict()
                messages_dict["entered_locations_core"] = None
                messages_dict["left_locations_core"] = None
                messages_dict["entered_location"] = "entering {} ".format(name)
                messages_dict["left_location"] = "leaving {} ".format(name)
                location_object.set_messages(messages_dict)
                chrani_bot.locations.upsert(location_object, save=True)

                chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You called your location {}".format(name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))

            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You can not name that which you do not have!!", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit location name",
        "usage": "/edit location name <location_identifier> = <location name>"
    },
    "action": set_up_location_name,
    "group": "locations",
    "essential": False
})


def change_location_visibility(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"make\slocation\s(?P<location_identifier>{lir})\s(?P<status>(public|private))$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            status_to_set = p.group("status") == 'public'
            try:
                location_object = chrani_bot.locations.get(source_player.steamid, identifier)
                if location_object.set_visibility(status_to_set):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You've made your location {} {}".format(location_object.name, 'public' if status_to_set else 'private'), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
                    chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
                    chrani_bot.locations.upsert(location_object, save=True)
                else:
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "A public location with the identifier {} already exists".format(location_object.identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You do not own that location :(", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "make location",
        "usage": "/make location <location_identifier> <'public' or 'private'>"
    },
    "action": change_location_visibility,
    "group": "locations",
    "essential": False
})


def set_up_location_outer_perimeter(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"edit\slocation\souter\sperimeter\s(?P<location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "I can not find a location called {}".format(identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            coord_tuple = target_player.get_coord_tuple()
            distance_to_location = location_object.get_distance(coords)
            set_radius, allowed_range = location_object.set_radius(distance_to_location)
            if set_radius is True:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the location {} ends here and spans {} meters ^^".format(identifier, int(location_object.radius * 2)), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            if location_object.radius <= location_object.warning_boundary:
                set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
                if set_radius is True:
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the inner core has been set to match the outer perimeter.", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                else:
                    return False

            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            chrani_bot.locations.upsert(location_object, save=True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit location outer perimeter",
        "usage": "/edit location outer perimeter <location_identifier>"
    },
    "action": set_up_location_outer_perimeter,
    "group": "locations",
    "essential": False
})


def set_up_location_inner_perimeter(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"edit\slocation\sinner\sperimeter\s(?P<location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "I can not find a location called {}".format(identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            coord_tuple = target_player.get_coord_tuple()
            distance_to_location = location_object.get_distance(coords)
            warning_boundary, allowed_range = location_object.set_warning_boundary(distance_to_location)
            if warning_boundary is True:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "the warning boundary {} ends here and spans {} meters ^^".format(identifier, int(location_object.warning_boundary * 2)), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "your given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(warning_boundary), int(allowed_range[0]), int(allowed_range[-1])), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            chrani_bot.locations.upsert(location_object, save=True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit location inner perimeter",
        "usage": "/edit location inner perimeter <location_identifier>"
    },
    "action": set_up_location_inner_perimeter,
    "group": "locations",
    "essential": False
})


def list_locations(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            available_locations_dict = {}
            location_objects_dict = chrani_bot.locations.get_available_locations(target_player)
            for location_identifier, location_object in location_objects_dict.iteritems():
                output_line = "{location_name} (id:[ffffff]{location_identifier}[-] coords:[ffffff]{pos_x} {pos_y} {pos_z}[-])".format(
                        location_name=location_object.name, location_identifier=location_identifier, pos_x=location_object.pos_x, pos_y=location_object.pos_y, pos_z=location_object.pos_z
                    )

                chat_color = chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning") if location_object.is_public else chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success")
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, output_line, color=chat_color)

            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "[{color_public}]public [-] / [{color_private}] private [-]".format(color_public=chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"), color_private=chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning")))
        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "{} can not list that which you do not have!".format(target_player.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "available locations",
        "usage": "/available locations"
    },
    "action": list_locations,
    "group": "locations",
    "essential": False
})


def goto_location(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"goto\slocation\s({lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            location_identifier = p.group(1)
            try:
                locations_dict = chrani_bot.locations.get_available_locations(target_player)
                try:
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, location_object=locations_dict[location_identifier])
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You have ported to the location {}".format(location_identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                except IndexError:
                    raise KeyError

            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "The location {} is not available to you :(".format(location_identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("error"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "goto location",
        "usage": "/goto location <location_identifier>"
    },
    "action": goto_location,
    "group": "locations",
    "essential": False
})


def remove_location(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\slocation\s({lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group(1)
            location_name_is_not_reserved = False
            if identifier in ["teleport", "lobby", "spawn", "home", "death"]:
                message = "{} is a reserved name. Aborted!.".format(identifier)
                response_messages.add_message(message, False)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
            else:
                location_name_is_not_reserved = True

            location_name_in_use = False
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
                location_name_in_use = True
            except KeyError:
                message = "I have never heard of a location called {}".format(identifier)
                response_messages.add_message(message, False)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            if location_name_is_not_reserved and location_name_in_use:
                chrani_bot.locations.remove(target_player.steamid, identifier)
                chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
                message = "{} deleted location {}".format(target_player.name, identifier)
                response_messages.add_message(message, False)
                chrani_bot.socketio.emit('remove_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
            else:
                message = "Location {} could not be removed :(".format(identifier)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
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
        "trigger": "remove location",
        "usage": "/remove location <location_identifier>"
    },
    "action": remove_location,
    "group": "locations",
    "essential": False
})


def protect_inner_core(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"enable\slocation\sprotection\s({lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group(1)
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "coming from the wrong end... set up the location first!", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            if location_object.set_protected_core(True):
                chrani_bot.locations.upsert(location_object, save=True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "The location {} is now protected!".format(location_object.identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "could not enable protection for location {} :(".format(location_object.identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "enable location protection",
        "usage": "/enable location protection <location_identifier>"
    },
    "action": protect_inner_core,
    "group": "locations",
    "essential": False
})


def unprotect_inner_core(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"disable\slocation\sprotection\s({lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group(1)
            try:
                location_object = chrani_bot.locations.get(target_player.steamid, identifier)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "coming from the wrong end... set up the location first!", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                return False

            if location_object.set_protected_core(False):
                chrani_bot.locations.upsert(location_object, save=True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "The location {} is now unprotected!".format(location_object.identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
            else:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "could not disable protection for location {} :(".format(location_object.identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "disable location protection",
        "usage": "/disable location protection <location_identifier>"
    },
    "action": unprotect_inner_core,
    "group": "locations",
    "essential": False
})


def change_perimeter_warning(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"make\slocation\s(?P<location_identifier>{lir})\s(?P<status>(warn\son\souter|warn\son\sboth|never\swarn))$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            status_to_set = p.group("status")
            try:
                location_object = chrani_bot.locations.get(source_player.steamid, identifier)
                if status_to_set == "warn on outer":
                    location_object.show_messages = True
                    location_object.show_warning_messages = False
                elif status_to_set == "warn on both":
                    location_object.show_messages = True
                    location_object.show_warning_messages = True
                elif status_to_set == "never warn":
                    location_object.show_messages = False
                    location_object.show_warning_messages = False

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Your location {} will {}".format(location_object.name, status_to_set), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
                chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
                chrani_bot.locations.upsert(location_object, save=True)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You do not own that location :(", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "make location",
        "usage": "/make location <location_identifier> <'warn on outer' or 'warn on both' or 'never warn'>"
    },
    "action": change_perimeter_warning,
    "group": "locations",
    "essential": False
})


def change_location_shape(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"make\slocation\s(?P<location_identifier>{lir})\sa\s(?P<shape>(sphere|cube|round\sarea|square\sarea))$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            shape_to_set = p.group("shape")
            try:
                location_object = chrani_bot.locations.get(source_player.steamid, identifier)
                if shape_to_set == "sphere":
                    location_object.set_shape("sphere")
                elif shape_to_set == "cube":
                    location_object.set_shape("cube")
                elif shape_to_set == "round area":
                    location_object.set_shape("circle")
                else:
                    location_object.set_shape("square")

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Your location {} is now {}".format(location_object.name, shape_to_set), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
                chrani_bot.locations.upsert(location_object, save=True)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You do not own that location :(", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "make location",
        "usage": "/make location <location_identifier> <'a sphere' or 'a cube' or 'a round area' or 'a square area'>"
    },
    "action": change_location_shape,
    "group": "locations",
    "essential": False
})


def change_location_type(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"make\slocation\s(?P<location_identifier>{lir})\sa\s(?P<type>(village|standard location|teleport))$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            identifier = p.group("location_identifier")
            type_to_set = p.group("type")
            try:
                location_object = chrani_bot.locations.get(source_player.steamid, identifier)
                if type_to_set == "village":
                    location_object.set_type("village")
                elif type_to_set == "teleport":
                    location_object.set_type("teleport")
                else:
                    location_object.set_type("standard")

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "Your location {} is now {}".format(location_object.name, type_to_set), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
                chrani_bot.socketio.emit('update_leaflet_markers', chrani_bot.locations.get_leaflet_marker_json([location_object]), namespace='/chrani-bot/public')
                chrani_bot.locations.upsert(location_object, save=True)
            except KeyError:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You do not own that location :(", chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "make location",
        "usage": "/make location <location_identifier> <'a village' or 'a teleport' or 'a standard location'>"
    },
    "action": change_location_type,
    "group": "locations",
    "essential": False
})
