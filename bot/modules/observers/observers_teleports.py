import common


def player_entered_teleport(chrani_bot, player_observer):
    try:
        player_object = chrani_bot.players.get_by_steamid(player_observer.player_steamid)
        locations_dict = dict((k, v) for k, v in chrani_bot.locations.get('system').iteritems() if v.teleport_active is True)
    except KeyError:
        return

    for location_identifier, location_object in locations_dict.iteritems():
        """ go through each 'system' location and check if the player is inside """
        for player_status, status in location_object.get_player_status(player_object).iteritems():
            if player_status == "has entered core" or player_status == "is inside core":
                if location_object.teleport_active is True and location_object.teleport_target is not None:
                    target_location_object = chrani_bot.locations.get('system', location_object.teleport_target)
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_object, coord_tuple=target_location_object.get_teleport_coords_tuple())

        chrani_bot.locations.upsert(location_object)


common.observers_dict["player_entered_teleport"] = {
    "type": "monitor",
    "title": "player crossed teleport boundary",
    "action": player_entered_teleport,
}


common.observers_controller["player_entered_teleport"] = {
    "is_active": True,
    "is_essential": False
}
