from location import Location

actions_dev = []


def set_up_lobby(self, player_object, locations):
    location_dict = dict(
        owner='server',
        name='lobby',
        description="Tha Lobby",
        pos_x=int(117),
        pos_y=int(111),
        pos_z=int(-473),
        shape='sphere',
        radius=16,
        boundary_percentage=50,
        region=None
    )
    locations.update({'lobby': Location(**location_dict)})

    self.tn.send_message_to_player(player_object, "a lobby has been set up for testing!")
    self.tn.send_message_to_player(player_object, "use '/password openup' to get authenticated.")
    self.tn.send_message_to_player(player_object, "use '/password whatever' to be treated like a new player again!")


actions_dev.append(("isequal", "set up dev-lobby", set_up_lobby, "(self, player_object, locations)"))

def set_up_homes(self, player_object, locations):
    location_dict = dict(
        owner='ecv',
        name="home",
        description="Ecv's Casa",
        pos_x=int(246),
        pos_y=int(62),
        pos_z=int(825),
        shape='sphere',
        radius=15,
        boundary_percentage=33,
        region=['0.1.7rg']
    )
    locations.update({'76561198040658370': {"home": Location(**location_dict)}})

    location_dict = dict(
        owner='LadyAni',
        name="home",
        description="LadyAni's crib",
        pos_x=int(116),
        pos_y=int(77),
        pos_z=int(-428),
        shape='sphere',
        radius=15,
        boundary_percentage=33,
        region=['0.1.7rg']
    )
    locations.update({'76561198040548018': {"home": Location(**location_dict)}})

    location_dict = dict(
        owner='ReflexTR',
        name="home",
        description="Reflexes Hideout",
        pos_x=int(137),
        pos_y=int(75),
        pos_z=int(-436),
        shape='sphere',
        radius=8,
        boundary_percentage=50,
        region=['0.1.7rg']
    )
    locations.update({'76561198010873208': {"home": Location(**location_dict)}})

    self.tn.send_message_to_player(player_object, "some homes have been set up for testing!")


actions_dev.append(("isequal", "set up dev-homes", set_up_homes, "(self, player_object, locations)"))