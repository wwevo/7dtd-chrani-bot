from bot.modules.logger import logger
import time
import common
import threading


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_lobby_boundary(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
    except KeyError:
        return False

    if player_object.authenticated is True:
        return

    try:
        location_object = self.bot.locations.get('system', "lobby")
    except KeyError:
        return False

    if location_object.enabled is True and not location_object.player_is_inside_boundary(player_object) and player_object.initialized:
        def teleport_worker():
            seconds = 2
            self.bot.tn.send_message_to_player(player_object, "You will be ported to the lobby in {seconds} seconds!".format(seconds=seconds), color=self.bot.chat_colors['warning'])
            time.sleep(seconds)

            if not location_object.player_is_inside_boundary(player_object) and self.bot.tn.teleportplayer(player_object, location_object=location_object):
                player_object.set_coordinates(location_object)
                self.bot.players.upsert(player_object)
                logger.info("{} has been ported to the lobby!".format(player_object.name))
                self.bot.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>", color=self.bot.chat_colors['warning'])
                self.bot.tn.send_message_to_player(player_object, self.bot.settings.get_setting_by_name(name="basic_server_info", default="see https://chrani.net for more information!", color=self.bot.chat_colors['warning']))

            time.sleep(seconds)
            player_object.active_teleport_thread = False
            return True

        if not player_object.active_teleport_thread:
            player_object.active_teleport_thread = True
            teleport_thread = threading.Thread(target=teleport_worker)
            teleport_thread.start()


common.observers_dict["player_is_outside_lobby_boundary"] = {
    "type": "monitor",
    "title": "player left lobby",
    "action": player_is_outside_lobby_boundary,
    "env": "(self)",
    "essential": True
}


common.observers_controller["player_is_outside_lobby_boundary"] = {
    "is_active": True
}
