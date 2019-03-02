from bot.modules.logger import logger
import time
import common
import threading


# the only lobby specific observer. since it is a location, generic global_observer can be found in observers_locations
def player_is_outside_lobby_boundary(chrani_bot, player_object):
    try:
        player_object = chrani_bot.players.get_by_steamid(player_object.player_steamid)
    except KeyError:
        return False

    if chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("authenticated", False):
        return

    try:
        location_object = chrani_bot.locations.get('system', "lobby")
    except KeyError:
        return False

    if location_object.enabled is True and not location_object.position_is_inside_boundary(player_object.get_coord_tuple()) and chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("is_initialized", False):
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_object, location_object=location_object, delay=3)


common.observers_dict["player_is_outside_lobby_boundary"] = {
    "type": "monitor",
    "title": "player left lobby",
    "action": player_is_outside_lobby_boundary
}


common.observers_controller["player_is_outside_lobby_boundary"] = {
    "is_active": True,
    "is_essential": True
}
