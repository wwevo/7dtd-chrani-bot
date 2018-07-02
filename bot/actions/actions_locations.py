import re

from bot.objects.location import Location
from bot.modules.logger import logger

actions_locations = []


def set_up_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"add\slocation\s(?P<location_name>[\W\w\s]{1,19})$", command)
        if p:
            name = p.group("location_name")
            if name in ["teleport", "lobby", "spawn", "home", "death"]:
                self.tn.send_message_to_player(player_object, "{} is a reserved name. Aborted!.".format(name), color=self.bot.chat_colors['warning'])
                raise KeyError

            location_object = Location()
            location_object.radius = float(self.bot.get_setting_by_name("location_default_radius"))
            location_object.warning_boundary = float(self.bot.get_setting_by_name("location_default_radius")) * float(self.bot.get_setting_by_name("location_default_warning_boundary_ratio"))

            location_object.set_coordinates(player_object)
            location_object.set_name(name)
            identifier = location_object.set_identifier(name)  # generate the identifier from the name
            location_object.set_owner(player_object.steamid)
            location_object.set_shape("sphere")

            messages_dict = location_object.get_messages_dict()
            messages_dict["entering_core"] = None
            messages_dict["leaving_core"] = None
            messages_dict["entering_boundary"] = "you have entered the location {}".format(name)
            messages_dict["leaving_boundary"] = "you have left the location {}".format(name)

            location_object.set_messages(messages_dict)
            location_object.set_list_of_players_inside([player_object.steamid])

            self.bot.locations.upsert(location_object, save=True)

            self.tn.send_message_to_player(player_object, "You have created a location, it is stored as {} and spans {} meters.".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
            self.tn.send_message_to_player(player_object, "use '{}' to access it with commands like /edit location name {} = Whatever the name shall be".format(identifier, identifier), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
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
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location teleport",
        "usage" : "/edit location teleport <location_identifier>"
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
                messages_dict["entering_core"] = None
                messages_dict["leaving_core"] = None
                messages_dict["entering_boundary"] = "entering {} ".format(name)
                messages_dict["leaving_boundary"] = "leaving {} ".format(name)
                location_object.set_messages(messages_dict)
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "You called your location {}".format(name), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "You can not name that which you do not have!!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location name",
        "usage" : "/edit location name <location_identifier> = <location name>"
    },
    "action" : set_up_location_name,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def change_location_visibility(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"make\splayers\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\slocation\s(?P<identifier>[\W\w\s]{1,19})\s(?P<status>(public|private))$", command)
        if p:
            identifier = p.group("identifier")
            status_to_set = p.group("status") == 'public'

            location_owner_steamid = p.group("steamid")
            location_owner_entityid = p.group("entityid")
            if location_owner_steamid is None:
                location_owner_steamid = self.bot.players.entityid_to_steamid(location_owner_entityid)
                if location_owner_steamid is False:
                    self.tn.send_message_to_player(player_object, "could not find player", color=self.bot.chat_colors['error'])
                    return False

            location_owner = self.bot.players.get(location_owner_steamid)
            try:
                location_object = self.bot.locations.get(location_owner.steamid, identifier)
                if location_object.set_visibility(status_to_set):
                    self.tn.send_message_to_player(player_object, "You've made your location {} {}".format(location_object.name, p.group("status")), color=self.bot.chat_colors['background'])
                    self.bot.locations.upsert(location_object, save=True)
                else:
                    self.tn.send_message_to_player(player_object, "A public location with the identifier {} already exists".format(location_object.identifier), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "You do not own that location :(", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "make players",
        "usage" : "/make players <steamid/entityid> location <location_identifier> <'public' or 'private'>"
    },
    "action" : change_location_visibility,
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

            coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)
            distance_to_location = location_object.get_distance(coords)
            set_radius, allowed_range = location_object.set_radius(distance_to_location)
            if set_radius is True:
                self.tn.send_message_to_player(player_object, "the location {} ends here and spans {} meters ^^".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "you given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(set_radius), int(allowed_range[0]), int(allowed_range[-1])), color=self.bot.chat_colors['warning'])
                return False

            if location_object.radius <= location_object.warning_boundary:
                set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
                if set_radius is True:
                    self.tn.send_message_to_player(player_object, "the inner core has been set to match the outer perimeter.", color=self.bot.chat_colors['warning'])
                else:
                    return False

            self.bot.locations.upsert(location_object, save=True)

    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location outer perimeter",
        "usage" : "/edit location outer perimeter <location_identifier>"
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

            coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)
            distance_to_location = location_object.get_distance(coords)
            warning_boundary, allowed_range = location_object.set_warning_boundary(distance_to_location)
            if warning_boundary is True:
                self.tn.send_message_to_player(player_object, "the warning boundary {} ends here and spans {} meters ^^".format(identifier, int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "your given radius of {} seems to be invalid, allowed radius is {} to {} meters".format(int(warning_boundary), int(allowed_range[0]), int(allowed_range[-1])), color=self.bot.chat_colors['warning'])
                return False

            self.bot.locations.upsert(location_object, save=True)

    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit location inner perimeter",
        "usage" : "/edit location inner perimeter <location_identifier>"
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
            output_list = []
            location_objects_dict = self.bot.locations.get_available_locations(player_object)
            for name, location_object in location_objects_dict.iteritems():
                output_list.append("{} @ ({} x:{}, y:{}, z:{}) - {}".format(location_object.name, location_object.identifier, location_object.pos_x, location_object.pos_y, location_object.pos_z, 'public' if location_object.is_public else 'private'))

            for output_line in output_list:
                self.tn.send_message_to_player(player_object, output_line)

        except KeyError:
            self.tn.send_message_to_player(player_object, "{} can not list that which you do not have!".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "available locations",
        "usage" : "/available locations"
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
            location_identifier = p.group(1)
            try:
                locations_dict = self.bot.locations.get_available_locations(player_object)
                try:
                    if locations_dict[location_identifier].enabled is True and self.tn.teleportplayer(player_object, location_object=locations_dict[location_identifier]):
                        self.tn.send_message_to_player(player_object, "You have ported to the location {}".format(location_identifier), color=self.bot.chat_colors['success'])
                    else:
                        self.tn.send_message_to_player(player_object, "Teleporting to location {} failed :(".format(location_identifier), color=self.bot.chat_colors['error'])
                except IndexError:
                    raise KeyError

            except KeyError:
                self.tn.send_message_to_player(player_object, "You do not have access to that location with this command.".format(location_identifier), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "goto location",
        "usage" : "/goto location <location_identifier>"
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
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "remove location",
        "usage" : "/remove location <location_identifier>"
    },
    "action" : remove_location,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def protect_inner_core(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"enable\slocation\sprotection\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the location first!", color=self.bot.chat_colors['warning'])
                return False

        if location_object.set_protected_core(True):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The location {} is now protected!".format(location_object.identifier), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "could not enable protection for location {} :(".format(location_object.identifier), color=self.bot.chat_colors['warning'])

    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "enable location protection",
        "usage" : "/enable location protection <location_identifier>"
    },
    "action" : protect_inner_core,
    "env": "(self, command)",
    "group": "locations",
    "essential" : False
})


def unprotect_inner_core(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"disable\slocation\sprotection\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
            except KeyError:
                self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the location first!", color=self.bot.chat_colors['warning'])
                return False

        if location_object.set_protected_core(False):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The location {} is now unprotected!".format(location_object.identifier), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "could not disable protection for location {} :(".format(location_object.identifier), color=self.bot.chat_colors['warning'])

    except Exception as e:
        logger.exception(e)
        pass


actions_locations.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "disable location protection",
        "usage" : "/disable location protection <location_identifier>"
    },
    "action" : unprotect_inner_core,
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
        locations_dict = self.bot.locations.locations_dict
        for location_owner_steamid in locations_dict:
            """ go through each location and check if the player is inside
            locations are stored on a player-basis so we can have multiple 'home' and 'spawn' location and whatnot
            so we have to loop through every player_location_dict to get to the actual locations
            """
            for location_name, location_object in locations_dict[location_owner_steamid].iteritems():
                if player_object.region not in location_object.region_list:
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
                get_player_status = location_object.get_player_status(player_object)
                if get_player_status == "is outside" or get_player_status is None:
                    continue

                # self.tn.send_message_to_player(player_object, get_player_status + location_object.name)
                if get_player_status == "has left":
                    if location_object.messages_dict["leaving_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_boundary"], color=self.bot.chat_colors['background'])
                if get_player_status == "has entered":
                    if location_object.messages_dict["entering_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_boundary"], color=self.bot.chat_colors['warning'])
                if get_player_status == "has left core":
                    if location_object.messages_dict["leaving_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_core"], color=self.bot.chat_colors['warning'])
                if get_player_status == "is inside core":
                    if location_object.protected_core is True and player_object.steamid != location_object.owner:
                        if self.tn.teleportplayer(player_object, coord_tuple=location_object.eject_player(player_object)):
                            self.tn.send_message_to_player(player_object, "you have been ejected from {}'s protected core!".format(location_object.name), color=self.bot.chat_colors['warning'])
                if get_player_status == "has entered core":
                    if location_object.messages_dict["entering_core"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_core"], color=self.bot.chat_colors['warning'])

                self.bot.locations.upsert(location_object)
    except Exception as e:
        logger.exception(e)
        pass


observers_locations.append({
    "type" : "monitor",
    "title" : "player crossed location boundary",
    "action" : player_crossed_boundary,
    "env": "(self)",
    "essential" : True
})
