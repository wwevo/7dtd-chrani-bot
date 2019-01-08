from bot.objects.location import Location
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common


def on_player_death(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, 'death')
        except KeyError:
            location_name = 'Place of Death'
            location_dict = dict(
                identifier='death',
                name=location_name,
                description="{}'s {}".format(target_player.name, location_name),
                owner=target_player.steamid,
                shape='sphere',
                region=None,
                show_messages=False
            )
            location_object = Location(**location_dict)

        location_object.set_coordinates(target_player)
        location_object.set_radius(5)
        location_object.set_warning_boundary(3)

        try:
            chrani_bot.locations.upsert(location_object, save=True)
        except:
            return False

        target_player.is_initialized = False
        chrani_bot.players.upsert(target_player, save=True)
        message = "{}s place of death has been recorded ^^".format(target_player.name)
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))
        response_messages.add_message(message, True)

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
"group": "backpack",
    "essential": False
})


def on_player_kill(chrani_bot, source_player, target_player, command):
    try:
        return on_player_death(chrani_bot, source_player, target_player, command)

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
"group": "backpack",
    "essential": False
})


def take_me_to_my_backpack(chrani_bot, source_player, target_player, command):
    """Teleports a player to their place of death

    Keyword arguments:
    self -- the bot

    expected bot command:
    /take me to my pack

    example:
    /take me to my pack

    notes:
    a place of death must exist
    will not port if already near the pack
    the place of death will be removed after a successful teleport
    """
    try:
        response_messages = ResponseMessage()
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, "death")
            if location_object.player_is_inside_boundary(target_player):
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "eh, you already ARE near your pack oO".format(target_player.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
            else:
                coord_tuple = (location_object.pos_x, -1, location_object.pos_z)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", target_player, coord_tuple=coord_tuple)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", "{} can't live without their stuff".format(target_player.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("standard"))

            chrani_bot.locations.remove(target_player.steamid, 'death')

            message = "{}s place of death has been removed ^^".format(target_player.name)
            response_messages.add_message(message, True)

        except KeyError:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, "I don't have your last death on record, sorry :(".format(target_player.name), chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "take me to my pack",
        "usage": "/take me to my pack"
    },
    "action": take_me_to_my_backpack,
    "group": "backpack",
    "essential": False
})
