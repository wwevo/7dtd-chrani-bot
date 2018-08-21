from bot.modules.logger import logger
import common


def player_crossed_boundary(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        locations_dict = self.bot.locations.locations_dict
        for location_owner_steamid in locations_dict:
            """ go through each location and check if the player is inside
            locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
            so we have to loop through every player_location_dict to get to the actual locations
            """
            for location_name, location_object in locations_dict[location_owner_steamid].iteritems():
                # if player_object.region not in location_object.region_list:
                #
                # we only need to check a location if a player is near it
                #     continue

                """ different status-conditions for a player
                'has entered'
                'is inside'
                'has entered core'
                'is inside core'
                'has left core'
                'has left'
                'is outside'
                """
                for player_status, status in location_object.get_player_status(player_object).iteritems():
                    if player_status == "is inside core":
                        if location_object.protected_core is True:
                            if any(x in ["admin", "mod"] for x in player_object.permission_levels):
                                continue
                            elif player_object.steamid == location_object.owner:
                                continue
                            elif location_object.owner in player_object.playerfriends_list:
                                continue
                            elif player_object.steamid in location_object.protected_core_whitelist:
                                continue
                            else:
                                if self.tn.teleportplayer(player_object, coord_tuple=location_object.get_ejection_coords_tuple(player_object)):
                                    self.tn.send_message_to_player(player_object, "you have been ejected from {}'s protected core owned by {}!".format(location_object.name, location_object.owner), color=self.bot.chat_colors['warning'])
                    if player_status == "has left":
                        self.bot.socketio.emit('refresh_locations', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                        if location_object.messages_dict["left_location"] is not None:
                            self.tn.send_message_to_player(player_object, location_object.messages_dict["left_location"], color=self.bot.chat_colors['background'])
                    if player_status == "has left core":
                        self.bot.socketio.emit('refresh_locations', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                        if location_object.messages_dict["left_locations_core"] is not None:
                            self.tn.send_message_to_player(player_object, location_object.messages_dict["left_locations_core"], color=self.bot.chat_colors['background'])
                    if player_status == "has entered":
                        self.bot.socketio.emit('refresh_locations', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                        if location_object.messages_dict["entered_location"] is not None:
                            self.tn.send_message_to_player(player_object, location_object.messages_dict["entered_location"], color=self.bot.chat_colors['warning'])
                    if player_status == "has entered core":
                        self.bot.socketio.emit('refresh_locations', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
                        if location_object.messages_dict["entered_locations_core"] is not None:
                            self.tn.send_message_to_player(player_object, location_object.messages_dict["entered_locations_core"], color=self.bot.chat_colors['warning'])

                self.bot.locations.upsert(location_object)
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "player crossed location boundary",
    "action": player_crossed_boundary,
    "env": "(self)",
    "essential": True
})
