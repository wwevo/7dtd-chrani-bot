from location import Location

actions_dev = []


def set_up_locations(self, player_object, locations):
    location_dict = dict(
        name='lobby',
        description="Tha Lobby",
        owner=None,
        pos_x=int(117),
        pos_y=int(111),
        pos_z=int(-473),
        shape='sphere',
        radius=16,
        region=None
    )
    locations.update({'lobby': Location(**location_dict)})
    self.tn.send_message_to_player(player_object, "a lobby has been set up for testing!")

    location_dict = dict(
        name="home",
        description="Ecv's Casa",
        owner='ecv',
        pos_x=int(512),
        pos_y=int(61),
        pos_z=int(944),
        shape='sphere',
        radius=25,
        region=['1.1.7rg']
    )
    locations.update({'ecv': {"home": Location(**location_dict)}})
    self.tn.send_message_to_player(player_object, "a home has been set up for testing!")

    self.tn.send_message_to_player(player_object, "use '/password openup' to get authenticated.")
    self.tn.send_message_to_player(player_object, "use '/password whatever' to be treated like a new player again!")


actions_dev.append(("isequal", "set up dev stuff", set_up_locations, "(self, player_object, locations)"))