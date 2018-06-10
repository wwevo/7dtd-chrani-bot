import re
from bot.location import Location
from bot.logger import logger

actions_locations = []


def set_up_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"add\slocation\s([\W\w\s]{1,19})$", command)
        if p:
            name = p.group(1)
            if name in ["teleport", "lobby", "spawn", "home", "death"]:
                self.tn.send_message_to_player(player_object, "{} is a reserved name. Aborted!.".format(name), color=self.bot.chat_colors['warning'])
                raise KeyError

            location_object = Location()
            location_object.set_coordinates(player_object)
            location_object.set_name(name)
            identifier = location_object.set_identifier(name)  # generate the identifier from the name
            location_object.set_owner(player_object.steamid)
            location_object.set_shape("sphere")
            #location_object.set_region([player_object.region])
            # TODO: this seems like a crappy solution ^^ need a way more elegant... way
            messages_dict = location_object.get_messages_dict()
            messages_dict["entering_core"] = "entering {}'s core".format(name)
            messages_dict["leaving_core"] = "leaving {}'s core".format(name)
            messages_dict["entering_boundary"] = "entering {}".format(name)
            messages_dict["leaving_boundary"] = "leaving {}".format(name)
            location_object.set_messages(messages_dict)
            location_object.set_list_of_players_inside([player_object.steamid])
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "You have created a location, it is stored as {} and spans {} meters.".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
            self.tn.send_message_to_player(player_object, "use '{}' to access it with commands like /edit location name {} = Whatever the name shall be".format(identifier, identifier), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "add location",
        "usage" : "/add location <location name>"
    },
    "action" : set_up_location,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def set_up_location_teleport(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"edit\slocation\steleport\s(?P<identifier>[\W\w\s]{1,19})$", command)
        if p:
            identifier = p.group("identifier")
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the location first!", color=self.bot.chat_colors['warning'])
                return False

            if location_object.set_teleport_coordinates(player_object):
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the teleport for {} has been set up!".format(identifier), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "your position seems to be outside the location", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location teleport",
        "usage" : "/edit location teleport <identifier>"
    },
    "action" : set_up_location_teleport,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def set_up_location_name(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"edit\slocation\sname\s(?P<identifier>[\W\w\s]{1,19})\s=\s(?P<name>[\W\w\s]{1,19})$", command)
        if p:
            identifier = p.group("identifier")
            name = p.group("name")
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
                location_object.set_name(name)
                messages_dict = location_object.get_messages_dict()
                messages_dict["entering_core"] = "entering {}'s core area ".format(name)
                messages_dict["leaving_core"] = "leaving {}'s core area ".format(name)
                messages_dict["entering_boundary"] = "entering {} ".format(name)
                messages_dict["leaving_boundary"] = "leaving {} ".format(name)
                location_object.set_messages(messages_dict)
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "You called your location {}".format(name), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "You can not name that which you do not have!!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location name",
        "usage" : "/edit location teleport <location identifier>"
    },
    "action" : set_up_location_name,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def set_up_location_outer_perimeter(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"edit\slocation\souter\sperimeter\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier), color=self.bot.chat_colors['warning'])
                return False

            set_radius, allowed_range = location_object.set_radius(player_object)
            if set_radius is True:
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the location {} ends here and spans {} meters ^^".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location outer perimeter",
        "usage" : "/edit location outer perimeter <identifier>"
    },
    "action" : set_up_location_outer_perimeter,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def set_up_location_inner_perimeter(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"edit\slocation\sinner\sperimeter\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier), color=self.bot.chat_colors['warning'])
                return False

            set_radius, allowed_range = location_object.set_warning_boundary(player_object)
            if set_radius is True:
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the warning boundary {} ends here and spans {} meters ^^".format(identifier, int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location inner perimeter",
        "usage" : "/edit location inner perimeter <identifier>"
    },
    "action" : set_up_location_inner_perimeter,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def list_locations(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_objects_dict = self.bot.locations.get(player_object.steamid)
            for name, location_object in location_objects_dict.iteritems():
                self.tn.send_message_to_player(player_object, "{} @ ({} x:{}, y:{}, z:{})".format(location_object.name, location_object.identifier, location_object.pos_x, location_object.pos_y, location_object.pos_z))

        except KeyError:
            self.tn.send_message_to_player(player_object, "{} can not list that which you do not have!".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "my locations",
        "usage" : "/my locations"
    },
    "action" : list_locations,
    "env": "(self)",
    "group": "locations",
    "essential" : False
})


def goto_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"goto\slocation\s([\w\s]{1,19})$", command)
        if p:
            name = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, name)
                self.tn.say("{} went to location {}".format(player_object.name, name), color=self.bot.chat_colors['background'])
                self.tn.teleportplayer(player_object, location_object)
            except KeyError:
                self.tn.send_message_to_player(player_object, "i have never heard of a location called {}".format(name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "goto location",
        "usage" : "/goto location <identifier>"
    },
    "action" : goto_location,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def remove_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"remove\slocation\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            if identifier in ["teleport", "lobby", "spawn", "home", "death"]:
                self.tn.send_message_to_player(player_object, "{} is a reserved name. Aborted!.".format(identifier), color=self.bot.chat_colors['warning'])
                raise KeyError

            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
                self.bot.locations.remove(player_object.steamid, identifier)
                self.tn.say("{} deleted location {}".format(player_object.name, identifier), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "I have never heard of a location called {}".format(identifier), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "remove location",
        "usage" : "/remove location <identifier>"
    },
    "action" : remove_location,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})
"""
here come the observers
"""
observers_locations = []


def player_crossed_boundary(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        for location_owner_steamid in self.bot.locations.locations_dict:
            """ go through each location and check if the player is inside
            locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
            so we have to loop through every player_location_dict to get to the actual locations
            """
            for location_name, location_object in self.bot.locations.locations_dict[location_owner_steamid].iteritems():
                if player_object.region not in location_object.region_list:
                    # we only need to check a location if a player is near it
                    continue

                """ different status-conditions for a player
                None = do nothing
                is inside
                has entered
                has entered core
                has left core
                has left
                """
                get_player_status = location_object.get_player_status(player_object)
                if get_player_status is None:
                    pass
                if get_player_status == "is inside":
                    pass
                if get_player_status == "has left":
                    if location_object.messages_dict["leaving_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_boundary"], color=self.bot.chat_colors['background'])
                    self.bot.locations.upsert(location_object, save=True)
                if get_player_status == "has entered":
                    if location_object.messages_dict["entering_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_boundary"], color=self.bot.chat_colors['warning'])
                    self.bot.locations.upsert(location_object, save=True)
                if get_player_status == "has left core":
                    if location_object.messages_dict["leaving_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_core"], color=self.bot.chat_colors['warning'])
                    self.bot.locations.upsert(location_object, save=True)
                if get_player_status == "has entered core":
                    if location_object.messages_dict["entering_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_core"], color=self.bot.chat_colors['warning'])
                    self.bot.locations.upsert(location_object, save=True)
    except Exception as e:
        logger.error(e)
        pass


observers_locations.append({
    "type" : "monitor",
    "title" : "player crossed boundary",
    "action" : player_crossed_boundary,
    "env": "(self)",
    "essential" : True
})
