"""
here come the observers
"""
observers_locations = []


def player_crossed_outside_boundary_from_outside(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, locations_dict in locations.locations_dict.iteritems():
        for name, location_object in locations_dict.iteritems():
            try:
                if location_object.player_crossed_outside_boundary_from_outside(player_object):
                    if location_object.messages_dict["entering_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_boundary"])
            except Exception:
                pass


observers_locations.append(("player crossed boundary from outside", player_crossed_outside_boundary_from_outside, "(self, players, locations)"))


def player_crossed_outside_boundary_from_inside(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, locations_dict in locations.locations_dict.iteritems():
        for name, location_object in locations_dict.iteritems():
            try:
                if location_object.player_crossed_outside_boundary_from_inside(player_object):
                    if location_object.messages_dict["leaving_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_boundary"])
            except Exception:
                pass


observers_locations.append(("player crossed boundary from inside", player_crossed_outside_boundary_from_inside, "(self, players, locations)"))


def player_crossed_inside_core_from_boundary(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, locations_dict in locations.locations_dict.iteritems():
        for name, location_object in locations_dict.iteritems():
            try:
                if location_object.player_crossed_inside_core_from_boundary(player_object):
                    if location_object.messages_dict["entering_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_core"])
            except Exception:
                pass


observers_locations.append(("player crossed core boundary from outside", player_crossed_inside_core_from_boundary, "(self, players, locations)"))


def player_crossed_inside_boundary_from_core(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, locations_dict in locations.locations_dict.iteritems():
        for name, location_object in locations_dict.iteritems():
            try:
                if location_object.player_crossed_inside_boundary_from_core(player_object):
                    if location_object.messages_dict["leaving_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_core"])
            except Exception:
                pass


observers_locations.append(("player crossed core boundary from inside", player_crossed_inside_boundary_from_core, "(self, players, locations)"))