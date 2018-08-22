from bot.modules.logger import logger
import common


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        if player_object.authenticated is True:
            return

        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        if location_object is not False and location_object.enabled is True and not location_object.player_is_inside_boundary(player_object):
            if self.tn.teleportplayer(player_object, location_object=location_object):
                player_object.set_coordinates(location_object)
                self.bot.players.upsert(player_object)
                logger.info("{} has been ported to the lobby!".format(player_object.name))
                self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>", color=self.bot.chat_colors['alert'])
                self.tn.send_message_to_player(player_object, "see https://chrani.net/chrani-bot for more information!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "player left lobby",
    "action": player_is_outside_boundary,
    "env": "(self)",
    "essential": True
})
