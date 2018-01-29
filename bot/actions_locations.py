import re
from bot.location import Location

actions_locations = []


def set_up_location(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"set up a location named (.+)", command)
        if p:
            name = p.group(1)
            location_object = Location()
            location_object.set_name(name)
            identifier = location_object.set_identifier(name)  # generate the identifier from the name
            location_object.set_owner(player_object.steamid)
            location_object.set_shape("sphere")
            location_object.set_coordinates(player_object)
            location_object.set_region([player_object.region])
            # TODO: this seems like a crappy solution ^^ need a way more elegant... way
            messages_dict = location_object.get_messages_dict()
            messages_dict["entering_core"] = "entering {}'s core".format(name)
            messages_dict["leaving_core"] = "leaving {}'s core".format(name)
            messages_dict["entering_boundary"] = "entering {}".format(name)
            messages_dict["leaving_boundary"] = "leaving {}".format(name)
            location_object.set_messages(messages_dict)
            location_object.set_list_of_players_inside([player_object.steamid])
            locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "You have created a location, it is stored as {} and spans {} meters.".format(identifier, int(location_object.radius * 2)))
            self.tn.send_message_to_player(player_object, "use {} to access it with commands like /set up name for {} as Whatever the name shall be".format(identifier, identifier))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_locations.append(("startswith", "set up a location named", set_up_location, "(self, players, locations, command)"))


def name_my_location(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"set up the name for location (.+)\sas\s(.+)", command)
        if p:
            identifier = p.group(1)
            name = p.group(2)
            try:
                location_object = locations.get(player_object.steamid, identifier)
                location_object.set_name(name)
                messages_dict = location_object.get_messages_dict()
                messages_dict["entering_core"] = "entering {}'s core area ".format(name)
                messages_dict["leaving_core"] = "leaving {}'s core area ".format(name)
                messages_dict["entering_boundary"] = "entering {} ".format(name)
                messages_dict["leaving_boundary"] = "leaving {} ".format(name)
                location_object.set_messages(messages_dict)
                locations.upsert(location_object, save=True)
                self.tn.say("{} called a location {}".format(player_object.name, name))
            except KeyError:
                self.tn.send_message_to_player(player_object, "You can not name that which you do not have!!")

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "set up the name for location", name_my_location, "(self, players, locations, command)"))


def set_up_location_boundary(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"set up the boundary for location (.+)", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier))
                return False

            set_radius, allowed_range = location_object.set_radius(player_object)
            if set_radius is True:
                locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object,
                                               "the location {} ends here and spans {} meters ^^".format(identifier,
                                                   int(location_object.radius * 2)))
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])))


    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "set up the boundary for location ", set_up_location_boundary, "(self, players, locations, command)"))


def set_up_location_area(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"set up the location (.+) as a room starting from south west going north (.+)and east (.+) and up (.+)", command)
        if p:
            identifier = p.group(1)
            length = p.group(2)
            width = p.group(3)
            height = p.group(4)
            try:
                location_object = locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier))
                return False

            set_width, allowed_range = location_object.set_width(width)
            set_length, allowed_range = location_object.set_length(length)
            set_height, allowed_range = location_object.set_height(height)
            if set_width is True and set_length is True and set_height is True:
                location_object.set_shape("room")
                location_object.set_center(player_object, location_object.width, location_object.length, location_object.height)
                locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object,
                                               "the location {} ends here and spans {} meters ^^".format(identifier,
                                                   int(location_object.radius * 2)))
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])))


    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "set up the location", set_up_location_area, "(self, players, locations, command)"))


def set_up_location_warning_boundary(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"set up a warning boundary for location (.+)", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier))
                return False

            set_radius, allowed_range = location_object.set_warning_boundary(player_object)
            if set_radius is True:
                locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object,
                                               "the warning boundary {} ends here and spans {} meters ^^".format(identifier,
                                                   int(location_object.warning_boundary * 2)))
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])))


    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "set up a warning boundary for location ", set_up_location_warning_boundary, "(self, players, locations, command)"))


def make_location_a_shape(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    p = re.search(r"make the location (.+) a (.+)", command)
    if p:
        name = p.group(1)
        shape = p.group(2)
        if player_object.authenticated:
            try:
                location_object = locations.get(player_object.steamid, name)
                if location_object.set_shape(shape):
                    locations.upsert(location_object, save=True)
                    self.tn.send_message_to_player(player_object,"{} is a {} now.".format(location_object.name, shape))
                else:
                    self.tn.send_message_to_player(player_object,"{} is not an allowed shape at this time!".format(shape))
                    return False

            except KeyError:
                self.tn.send_message_to_player(player_object, "You can not change that which you do not own!")
        else:
            self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "make the location", make_location_a_shape, "(self, players, locations, command)"))


def list_players_locations(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        try:
            location_objects_dict = locations.get(player_object.steamid)
            for name, location_object in location_objects_dict.iteritems():
                self.tn.send_message_to_player(player_object,"{} @ ({} x:{}, y:{}, z:{})".format(location_object.name, location_object.identifier, location_object.pos_x, location_object.pos_y, location_object.pos_z))

        except KeyError:
            self.tn.send_message_to_player(player_object, "{} can not list that which he does not have!".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("isequal", "list my locations", list_players_locations, "(self, players, locations)"))


def goto_location(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"goto location\s(.+)", command)
        if p:
            name = p.group(1)
            try:
                location_object = locations.get(player_object.steamid, name)
                self.tn.say("{} went to location {}".format(player_object.name, name))
                self.tn.teleportplayer(player_object, location_object)
            except KeyError:
                self.tn.send_message_to_player(player_object, "i have never heard of {}".format(name))

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_locations.append(("startswith", "goto location", goto_location, "(self, players, locations, command)"))
"""
here come the observers
"""
observers_locations = []


def player_crossed_boundary(self, players, locations):
    player_object = players.get(self.player_steamid)
    for location_owner_steamid in locations.locations_dict:
        """ go through each location and check if the player is inside
        locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
        so we have to loop through every player_location_dict to get to the actual locations
        """
        for location_name, location_object in locations.locations_dict[location_owner_steamid].iteritems():
            """ different status-conditions for a player
            None = do nothing
            is inside
            has entered
            has left
            """
            get_player_status = location_object.get_player_status(player_object)
            if get_player_status is None:
                pass
            if get_player_status == "is inside":
                pass
            if get_player_status == "has left":
                self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_boundary"])
                locations.upsert(location_object, save=True)
            if get_player_status == "has entered":
                self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_boundary"])
                locations.upsert(location_object, save=True)


observers_locations.append(("player crossed boundary", player_crossed_boundary, "(self, players, locations)"))
