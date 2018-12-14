import common


def player_crossed_location_boundary(chrani_bot, player_observer):
    locations_dict = chrani_bot.locations.locations_dict
    for location_owner_steamid in locations_dict:
        """ go through each location and check if the player is inside
        locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
        so we have to loop through every player_location_dict to get to the actual locations
        """
        for location_name, location_object in locations_dict[location_owner_steamid].iteritems():
            if player_observer.player_object.region not in location_object.region_list:
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
            for player_status, status in location_object.get_player_status(player_observer.player_object).iteritems():
                if player_status == "is inside core":
                    if location_object.protected_core is True:
                        if any(x in ["admin", "mod"] for x in player_observer.player_object.permission_levels):
                            pass  # continue
                        if player_observer.player_object.steamid == location_object.owner:
                            continue
                        elif location_object.owner in player_observer.player_object.playerfriends_list:
                            continue
                        elif player_observer.player_object.steamid in location_object.protected_core_whitelist:
                            continue
                        else:
                            if chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "teleportplayer", player_observer.player_object, coord_tuple=location_object.get_ejection_coords_tuple()):
                                location_object_owner = player_observer.players.get_by_steamid(location_object.owner)
                                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, "you have been ejected from {}'s protected core owned by {}!".format(location_object.name, location_object_owner.name), chrani_bot.chat_colors['warning'])
                                chrani_bot.socketio.emit('status_log', {"steamid": player_observer.player_object.steamid, "command": "{} has been ejected from {}'s protected core owned by {}!".format(player_observer.player_object.name, location_object.name, location_object_owner.name)}, namespace='/chrani-bot/public')

                update_table = False
                if player_status == "has left":
                    chrani_bot.locations.upsert(location_object, save=True)
                    update_table = True
                    if location_object.messages_dict["left_location"] is not None and location_object.show_messages is True and (location_object.owner in [player_observer.player_object.steamid, "system"] or (location_object.is_public or location_object.protected_core)):
                        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, location_object.messages_dict["left_location"], chrani_bot.chat_colors['standard'])
                if player_status == "has left core":
                    update_table = True
                    if location_object.messages_dict["left_locations_core"] is not None and location_object.show_warning_messages is True and (location_object.owner == player_observer.player_object.steamid or location_object.is_public):
                        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, location_object.messages_dict["left_locations_core"], chrani_bot.chat_colors['standard'])
                if player_status == "has entered":
                    chrani_bot.locations.upsert(location_object, save=True)
                    update_table = True
                    if location_object.messages_dict["entered_location"] is not None and location_object.show_messages is True and (location_object.owner in [player_observer.player_object.steamid, "system"] or (location_object.is_public or location_object.protected_core)):
                        if location_object.protected_core:
                            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, "{} ({})".format(location_object.messages_dict["entered_location"], "protected"), chrani_bot.chat_colors['error'])
                        else:
                            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, location_object.messages_dict["entered_location"], chrani_bot.chat_colors['warning'])
                if player_status == "has entered core":
                    update_table = True
                    if location_object.messages_dict["entered_locations_core"] is not None and (location_object.show_warning_messages is True or location_object.protected_core) and (location_object.owner == player_observer.player_object.steamid or location_object.is_public):
                        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, location_object.messages_dict["entered_locations_core"], chrani_bot.chat_colors['warning'])

                if update_table:
                    chrani_bot.locations.upsert(location_object)
                    chrani_bot.socketio.emit('refresh_locations', {"steamid": player_observer.player_object.steamid, "entityid": player_observer.player_object.entityid}, namespace='/chrani-bot/public')


common.observers_dict["player_crossed_location_boundary"] = {
    "type": "monitor",
    "title": "player crossed location boundary",
    "action": player_crossed_location_boundary
}

common.observers_controller["player_crossed_location_boundary"] = {
    "is_active": True,
    "is_essential": False
}
