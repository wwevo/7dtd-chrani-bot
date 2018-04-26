import re
from bot.location import Location
from bot.logger import logger

actions_lobby = []


def set_up_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        location_object = Location()
        location_object.set_owner('system')
        location_object.set_name('The Lobby')
        identifier = location_object.set_identifier('lobby')
        location_object.set_description('The \"there is no escape\" Lobby')
        location_object.set_shape("sphere")
        location_object.set_coordinates(player_object)
        location_object.set_region([player_object.region])
        messages_dict = location_object.get_messages_dict()
        messages_dict["entering_core"] = None
        messages_dict["leaving_core"] = None
        messages_dict["entering_boundary"] = None
        messages_dict["leaving_boundary"] = "leaving {}, you better be authenticated!!".format(identifier)
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([player_object.steamid])
        self.bot.locations.upsert(location_object, save=True)
        self.tn.send_message_to_player(player_object, "You have set up a lobby", color=self.bot.chat_colors['success'])
        self.tn.send_message_to_player(player_object, "Set up the perimeter with /set up lobby perimeter, while standing on the edge of it.".format(player_object.name), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("isequal", "set lobby", set_up_lobby, "(self)", "lobby"))


def set_up_lobby_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_radius(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "Your given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("isequal", "set lobby outer perimeter", set_up_lobby_perimeter, "(self)", "lobby"))


def set_up_lobby_warning_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_warning_boundary(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby-warnings will be issued from this point on", color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "Is this inside the lobby perimeter?", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("isequal", "set lobby inner perimeter", set_up_lobby_warning_perimeter, "(self)", "lobby"))


def remove_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            self.bot.locations.remove('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "no lobby found oO", color=self.bot.chat_colors['warning'])
            return False
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("isequal", "remove lobby", remove_lobby, "(self)", "lobby"))


def password(self, command):
    try:
        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"password\s(\w+)$", command)
        if p:
            pwd = p.group(1)
            if pwd in self.bot.passwords.values():
                try:
                    location_object = self.bot.locations.get(player_object.steamid, 'spawn')
                    self.tn.send_message_to_player(player_object, "You have been ported back to your original spawn!", color=self.bot.chat_colors['success'])
                    self.tn.teleportplayer(player_object, location_object)
                except KeyError:
                    self.tn.send_message_to_player(player_object, "I am terribly sorry, I seem to have misplaced your spawn, {}".format(player_object.name), color=self.bot.chat_colors['warning'])
                    return False
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("startswith", "password", password, "(self, command)", "lobby"))


# def set_up_lobby_area(self, command):
#     try:
#         player_object = self.bot.players.get(self.player_steamid)
#         p = re.search(r"set up the lobby as a room starting from south west going north (.+) and east (.+) and up (.+)", command)
#         if p:
#             length = p.group(1)
#             width = p.group(2)
#             height = p.group(3)
#             try:
#                 location_object = self.bot.locations.get('system', 'lobby')
#             except KeyError:
#                 self.tn.send_message_to_player(player_object, "I can not find a location called {}".format('lobby'), color=self.bot.chat_colors['warning'])
#                 return False
#
#             set_width, allowed_range = location_object.set_width(width)
#             set_length, allowed_range = location_object.set_length(length)
#             set_height, allowed_range = location_object.set_height(height)
#             if set_width is True and set_length is True and set_height is True:
#                 location_object.set_shape("room")
#                 location_object.set_center(player_object, location_object.width, location_object.length, location_object.height)
#                 self.bot.locations.upsert(location_object, save=True)
#                 self.tn.send_message_to_player(player_object, "the location {} ends here and spans {} meters ^^".format('lobby', int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
#             else:
#                 self.tn.send_message_to_player(player_object, "you given coordinates seem to be invalid", color=self.bot.chat_colors['warning'])
#     except Exception as e:
#         logger.error(e)
#         pass
#
#
# actions_lobby.append(("startswith", "set up the lobby", set_up_lobby_area, "(self, command)", "lobby"))


def set_up_lobby_teleport(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\slobby\steleport$", command)
        if p:
            try:
                location_object = self.bot.locations.get('system', 'lobby')
            except KeyError:
                self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the lobby first!", color=self.bot.chat_colors['warning'])
                return False

            if location_object.set_teleport_coordinates(player_object):
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the teleport for {} has been set up!".format('lobby'), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "your position seems to be outside of the location", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append(("startswith", "set lobby teleport", set_up_lobby_teleport, "(self, command)", "lobby"))


"""
here come the observers
"""
observers_lobby = []


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        if player_object.authenticated is not True and player_object.is_responsive:
            if not location_object.player_is_inside_boundary(player_object):
                if self.tn.teleportplayer(player_object, location_object):
                    player_object.set_coordinates(location_object)
                    self.bot.players.upsert(player_object)
                    logger.info("{} has been ported to the lobby!".format(player_object.name))
                    self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>", color=self.bot.chat_colors['alert'])
    except Exception as e:
        logger.error(e)
        pass


observers_lobby.append(("monitor", "player left lobby", player_is_outside_boundary, "(self)"))
