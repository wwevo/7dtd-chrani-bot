from bot.modules.logger import logger
import common


def player_crossed_boundary(self):
    locations_dict = self.bot.locations.locations_dict
    for location_owner_steamid in locations_dict:
        """ go through each location and check if the player is inside
        locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
        so we have to loop through every player_location_dict to get to the actual locations
        """
        for location_name, location_object in locations_dict[location_owner_steamid].iteritems():
            if self.player_object.region not in location_object.region_list:
                # we only need to check a location if a player is near it
                continue

            """ different status-conditions for a player
            'has entered'
            'is inside'
            'has entered core'
            'is inside core'
            'has left core'
            'has left'
            'is outside'
            """
            for player_status, status in location_object.get_player_status(self.player_object).iteritems():
                if player_status == "is inside core":
                    if location_object.protected_core is True:
                        if any(x in ["admin", "mod"] for x in self.player_object.permission_levels):
                            pass  # continue
                        if self.player_object.steamid == location_object.owner:
                            continue
                        elif location_object.owner in self.player_object.playerfriends_list:
                            continue
                        elif self.player_object.steamid in location_object.protected_core_whitelist:
                            continue
                        else:
                            if self.tn.teleportplayer(self.player_object, coord_tuple=location_object.get_ejection_coords_tuple()):
                                location_object_owner = self.bot.players.get_by_steamid(location_object.owner)
                                self.tn.send_message_to_player(self.player_object, "you have been ejected from {}'s protected core owned by {}!".format(location_object.name, location_object_owner.name), color=self.bot.chat_colors['warning'])
                                self.bot.socketio.emit('command_log', {"steamid": self.player_object.steamid, "command": "{} has been ejected from {}'s protected core owned by {}!".format(self.player_object.name, location_object.name, location_object_owner.name)}, namespace='/chrani-bot/public')

                update_table = False
                if player_status == "has left":
                    update_table = True
                    if location_object.messages_dict["left_location"] is not None and location_object.show_messages is True:
                        self.tn.send_message_to_player(self.player_object, location_object.messages_dict["left_location"], color=self.bot.chat_colors['background'])
                if player_status == "has left core":
                    update_table = True
                    if location_object.messages_dict["left_locations_core"] is not None and location_object.show_warning_messages is True:
                        self.tn.send_message_to_player(self.player_object, location_object.messages_dict["left_locations_core"], color=self.bot.chat_colors['background'])
                if player_status == "has entered":
                    update_table = True
                    if location_object.messages_dict["entered_location"] is not None and location_object.show_messages is True:
                        self.tn.send_message_to_player(self.player_object, location_object.messages_dict["entered_location"], color=self.bot.chat_colors['warning'])
                if player_status == "has entered core":
                    update_table = True
                    if location_object.messages_dict["entered_locations_core"] is not None and location_object.show_warning_messages is True:
                        self.tn.send_message_to_player(self.player_object, location_object.messages_dict["entered_locations_core"], color=self.bot.chat_colors['warning'])

                if update_table:
                    self.bot.socketio.emit('refresh_locations', {"steamid": self.player_object.steamid, "entityid": self.player_object.entityid}, namespace='/chrani-bot/public')

            self.bot.locations.upsert(location_object)


common.observers_list.append({
    "type": "monitor",
    "title": "player crossed location boundary",
    "action": player_crossed_boundary,
    "env": "(self)",
    "essential": True
})
