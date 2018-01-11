from location import Location

actions_dev = []


def set_up_locations(self, player_object, locations):
    if player_object.authenticated:
        location_dict = dict(
            name='Chrani-bot Lobby',
            owner=None,
            pos_x=int(117),
            pos_y=int(111),
            pos_z=int(-473),
            shape='sphere',
            radius=6,
            region=None
        )
        locations.update({'lobby': Location(**location_dict)})

        self.tn.say("a lobby has been set up for testing!")
        self.tn.say("use '/password whatever' to be treated like a new player again!")
    else:
        self.tn.say(player_object.name + " is no authorized no nope. should go read read!")


actions_dev.append(("isequal", "set up dev stuff", set_up_locations, "(self, player_object, locations)"))