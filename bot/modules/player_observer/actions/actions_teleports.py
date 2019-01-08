import re
from bot.objects.location import Location
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common

from bot.modules.player_observer.actions.actions_locations import location_identifier_regex


def set_up_teleport_point(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"add\steleport\s(?P<location_name>{lir})$".format(lir=location_identifier_regex), command)
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
            identifier = location_object.set_identifier(name)  # generate the identifier from the name
            try:
                location_object = location_object = chrani_bot.locations.get('system', identifier)
                message = "a location with the identifier {} already exists, moving it!".format(identifier)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)
            except KeyError:
                location_name_not_in_use = True

            if location_name_is_valid and location_name_is_not_reserved:
                location_object.set_coordinates(target_player)
                location_object.set_radius(3)
                location_object.set_warning_boundary(1)
                location_object.set_shape('sphere')

                location_object.set_owner('system')
                location_object.protected_core_whitelist = []
                location_object.show_messages = False

                messages_dict = location_object.get_messages_dict()
                messages_dict["entered_locations_core"] = None
                messages_dict["left_locations_core"] = None
                messages_dict["entered_location"] = "Entering a teleport area!"
                messages_dict["left_location"] = "Left the teleport area."

                location_object.set_messages(messages_dict)
                chrani_bot.locations.upsert(location_object, save=True)

                response_messages.add_message("A Teleport with the identifier {} has been created".format(identifier), True)

                # bot.socketio.emit('refresh_teleports', '', namespace='/chrani-bot/public')

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "You have created a teleport point, it is stored as {}.".format(identifier, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success")))
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "use '{}' to access it with commands like /connect teleport {} with {}2".format(identifier, identifier, identifier), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
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
        "trigger": "add teleport",
        "usage": "/add teleport <location name>"
    },
    "action": set_up_teleport_point,
    "group": "teleports",
    "essential": False
})


def connect_teleport(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"connect\steleport\s(?P<source_location_identifier>{lir})\swith\s(?P<target_location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()

            source_location_identifier = p.group("source_location_identifier")
            source_location_exists = False

            try:
                source_location_object = chrani_bot.locations.get('system', source_location_identifier)
                source_location_exists = True
            except KeyError:
                message = "The source location does not exist :("
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            target_location_identifier = p.group("target_location_identifier")
            target_location_exists = False

            try:
                target_location_object = chrani_bot.locations.get('system', target_location_identifier)
                target_location_exists = True
            except KeyError:
                message = "your target location does not exist :("
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            if source_location_exists and target_location_exists:
                message = "You have connected teleport point {} with {}".format(source_location_object.identifier, target_location_object.identifier)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("success"))
                response_messages.add_message(message, True)

                source_location_object.teleport_target = target_location_object.identifier
                chrani_bot.locations.upsert(source_location_object, save=True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "connect teleport",
        "usage": "/connect teleport <source_location_identifier> with <target_location_identifier>"
    },
    "action": connect_teleport,
    "group": "teleports",
    "essential": False
})


def activate_teleport(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"activate\steleport\s(?P<location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            source_location_identifier = p.group("location_identifier")
            source_location_exists = False
            try:
                source_location_object = chrani_bot.locations.get('system', source_location_identifier)
                source_location_exists = True
            except KeyError:
                message = "that location does not exist :("
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            if source_location_exists:
                target_location_identifier = source_location_object.teleport_target
                target_location_exists = False
                try:
                    target_location_object = chrani_bot.locations.get('system', target_location_identifier)
                    target_location_exists = True
                except KeyError:
                    message = "your target location does not exist :("
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                    response_messages.add_message(message, False)

                if target_location_exists:
                    source_location_object.teleport_active = True
                    message = "Your teleport has been activated"
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                    response_messages.add_message(message, True)
                    chrani_bot.locations.upsert(source_location_object, save=True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "activate teleport",
        "usage": "/activate teleport <location_identifier>"
    },
    "action": activate_teleport,
    "group": "teleports",
    "essential": False
})


def deactivate_teleport(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"deactivate\steleport\s(?P<location_identifier>{lir})$".format(lir=location_identifier_regex), command)
        if p:
            response_messages = ResponseMessage()
            source_location_identifier = p.group("location_identifier")
            source_location_exists = False
            try:
                source_location_object = chrani_bot.locations.get('system', source_location_identifier)
                source_location_exists = True
            except KeyError:
                message = "that location does not exist :("
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, False)

            if source_location_exists:
                source_location_object.teleport_active = False
                message = "Your teleport has been deactivated"
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
                response_messages.add_message(message, True)
                chrani_bot.locations.upsert(source_location_object, save=True)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "deactivate teleport",
        "usage": "/deactivate teleport <location_identifier>"
    },
    "action": deactivate_teleport,
    "group": "teleports",
    "essential": False
})
