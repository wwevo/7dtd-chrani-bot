import re
from bot.location import Location
from bot.logger import logger

actions_locations = []


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
    except KeyError:
        location_dict = dict(
            identifier='spawn',
            name='Place of Birth',
            owner=player_object.steamid,
            shape='point',
            radius=None,
            region=[player_object.region]
        )
        location_object = Location(**location_dict)
        location_object.set_coordinates(player_object)
        self.bot.locations.upsert(location_object, save=True)
        self.tn.send_message_to_player(player_object, "Your place of birth has been recorded ^^", color=self.bot.chat_colors['background'])


actions_locations.append(("isequal", "joined the game", on_player_join, "(self)", "locations"))


def set_up_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slocation\s([\w\s]{1,19})$", command)
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
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "You have created a location, it is stored as {} and spans {} meters.".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
            self.tn.send_message_to_player(player_object, "use {} to access it with commands like /name for {} = Whatever the name shall be".format(identifier, identifier), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append(("startswith", "set location", set_up_location, "(self, command)", "locations"))


def set_up_location_teleport(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slocation\steleport\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
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


actions_locations.append(("startswith", "set location teleport", set_up_location_teleport, "(self, command)", "locations"))


def set_up_location_name(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slocation\sname\s([\w\s]{1,19})\s=\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            name = p.group(2)
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
                self.tn.say("{} called a location {}".format(player_object.name, name), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "You can not name that which you do not have!!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append(("startswith", "set location name", set_up_location_name, "(self, command)", "locations"))


def set_up_location_outer_perimeter(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slocation\souter\sperimeter\s(([\w\s]{1,19}))$", command)
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


actions_locations.append(("startswith", "set location outer perimeter", set_up_location_outer_perimeter, "(self, command)", "locations"))


# def set_up_location_area(self, command):
#     try:
#         player_object = self.bot.players.get(self.player_steamid)
#         p = re.search(r"set up the location (.+) as a room starting from south west going north (.+) and east (.+) and up (.+)", command)
#         if p:
#             identifier = p.group(1)
#             length = p.group(2)
#             width = p.group(3)
#             height = p.group(4)
#             try:
#                 location_object = self.bot.locations.get(player_object.steamid, identifier)
#             except KeyError:
#                 self.tn.send_message_to_player(player_object, "I can not find a location called {}".format(identifier), color=self.bot.chat_colors['warning'])
#                 return False
#
#             set_width, allowed_range = location_object.set_width(width)
#             set_length, allowed_range = location_object.set_length(length)
#             set_height, allowed_range = location_object.set_height(height)
#             if set_width is True and set_length is True and set_height is True:
#                 location_object.set_shape("room")
#                 location_object.set_center(player_object, location_object.width, location_object.length, location_object.height)
#                 self.bot.locations.upsert(location_object, save=True)
#                 self.tn.send_message_to_player(player_object, "the location {} ends here and spans {} meters ^^".format(identifier, int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
#             else:
#                 self.tn.send_message_to_player(player_object, "you given coordinates seem to be invalid", color=self.bot.chat_colors['warning'])
#     except Exception as e:
#         logger.error(e)
#         pass
#
#
# actions_locations.append(("startswith", "set up the location", set_up_location_area, "(self, command)", "locations"))


def set_up_location_inner_perimeter(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slocation\sinner\sperimeter\s([\w\s]{1,19})$", command)
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


actions_locations.append(("startswith", "set location inner perimeter", set_up_location_inner_perimeter, "(self, command)", "locations"))


# def make_location_a_shape(self, command):
#     try:
#         player_object = self.bot.players.get(self.player_steamid)
#         p = re.search(r"make the location (.+) a (.+)", command)
#         if p:
#             name = p.group(1)
#             shape = p.group(2)
#             try:
#                 location_object = self.bot.locations.get(player_object.steamid, name)
#                 if location_object.set_shape(shape):
#                     self.bot.locations.upsert(location_object, save=True)
#                     self.tn.send_message_to_player(player_object, "{} is a {} now.".format(location_object.name, shape), color=self.bot.chat_colors['success'])
#                 else:
#                     self.tn.send_message_to_player(player_object, "{} is not an allowed shape at this time!".format(shape), color=self.bot.chat_colors['warning'])
#                     return False
#
#             except KeyError:
#                 self.tn.send_message_to_player(player_object, "You can not change that which you do not own!", color=self.bot.chat_colors['warning'])
#     except Exception as e:
#         logger.error(e)
#         pass
#
#
# actions_locations.append(("startswith", "make the location", make_location_a_shape, "(self, command)", "locations"))


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


actions_locations.append(("isequal", "my locations", list_locations, "(self)", "locations"))


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


actions_locations.append(("startswith", "goto location", goto_location, "(self, command)", "locations"))


def remove_location(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"remove\slocation\s([\w\s]{1,19})$", command)
        if p:
            identifier = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, identifier)
                self.bot.locations.remove(player_object.steamid, identifier)
                self.tn.say("{} deleted location {}".format(player_object.name, identifier), color=self.bot.chat_colors['background'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "I have never heard of a location called {}".format(identifier), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_locations.append(("startswith", "remove location", remove_location, "(self, command)", "locations"))
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
                    if location_object.messages_dict["leaving_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["leaving_boundary"], color=self.bot.chat_colors['background'])
                    self.bot.locations.upsert(location_object, save=True)
                if get_player_status == "has entered":
                    if location_object.messages_dict["entering_boundary"] is not None:
                        self.tn.send_message_to_player(player_object, location_object.messages_dict["entering_boundary"], color=self.bot.chat_colors['warning'])
                    self.bot.locations.upsert(location_object, save=True)
    except Exception as e:
        logger.error(e)
        pass


observers_locations.append(("monitor", "player crossed boundary", player_crossed_boundary, "(self)"))
