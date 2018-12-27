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

    if player_object.authenticated is True:
        return

    try:
        location_object = chrani_bot.locations.get('system', "lobby")
    except KeyError:
        return False

    if location_object.enabled is True and not location_object.player_is_inside_boundary(player_object) and player_object.initialized:
        def teleport_worker():
            if not location_object.player_is_inside_boundary(player_object):
                seconds = 4
                message = "You will be ported to the lobby in {seconds} seconds!".format(seconds=seconds)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object, message, chrani_bot.chat_colors['warning'])
                time.sleep(seconds)

                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_object, location_object=location_object)
                player_object.set_coordinates(location_object)
                message = "{} has been ported to the lobby!".format(player_object.name)
                logger.info(message)
                time.sleep(seconds * 3)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object, "You have been ported to the lobby! Authenticate with /password <password>", chrani_bot.chat_colors['warning'])
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object, chrani_bot.settings.get_setting_by_name(name="basic_server_info", default="see https://chrani.net for more information!"), chrani_bot.chat_colors['warning'])
                player_object.active_teleport_thread = False

                player_object.update()
                chrani_bot.players.upsert(player_object)

            return True

        if player_object.active_teleport_thread is False:
            player_object.active_teleport_thread = True
            player_object.update()
            chrani_bot.players.upsert(player_object)
            teleport_thread = threading.Thread(target=teleport_worker)
            teleport_thread.start()


common.observers_dict["player_is_outside_lobby_boundary"] = {
    "type": "monitor",
    "title": "player left lobby",
    "action": player_is_outside_lobby_boundary
}


common.observers_controller["player_is_outside_lobby_boundary"] = {
    "is_active": True,
    "is_essential": False
}
