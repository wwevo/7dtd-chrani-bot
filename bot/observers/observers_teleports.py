import common


def player_entered_teleport(self):
    player_object = self.bot.players.get_by_steamid(self.player_steamid)
    locations_dict = dict((k, v) for k, v in self.bot.locations.get('system').iteritems() if v.teleport_active is True)
    for location_identifier, location_object in locations_dict.iteritems():
        """ go through each location and check if the player is inside
        locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
        so we have to loop through every player_location_dict to get to the actual locations
        """
        for player_status, status in location_object.get_player_status(player_object).iteritems():
            if player_status == "has entered core" or player_status == "is inside core":
                if location_object.teleport_active is True and location_object.teleport_target is not None:
                    target_location_object = self.bot.locations.get('system', location_object.teleport_target)
                    self.tn.teleportplayer(player_object, coord_tuple=target_location_object.get_teleport_coords_tuple(player_object))

        self.bot.locations.upsert(location_object)


common.observers_list.append({
    "type": "monitor",
    "title": "player crossed teleport boundary",
    "action": player_entered_teleport,
    "env": "(self)",
    "essential": True
})
