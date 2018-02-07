import re
from bot.location import Location
from bot.logger import logger

actions_lobby = []


def set_up_lobby(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
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
        self.tn.send_message_to_player(player_object, "{} has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.".format(player_object.name), color='22c927')
    else:
        self.tn.send_message_to_player(player_object, "You need to enter the password to get access to sweet commands!", color='db500a')


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self)", "lobby"))


def set_up_lobby_perimeter(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color='db500a')
            return False

        if location_object.set_radius(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color='22c927')
        else:
            self.tn.send_message_to_player(player_object, "Your given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color='db500a')
    else:
        self.tn.say(player_object, player_object.name + " needs to enter the password to get access to commands!", color='db500a')


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self)", "lobby"))


def set_up_lobby_warning_perimeter(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color='db500a')
            return False

        if location_object.set_warning_boundary(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby-warnings will be issued from this point on", color='22c927')
        else:
            self.tn.send_message_to_player(player_object, "Is this inside the lobby perimeter?", color='db500a')
    else:
        self.tn.say(player_object, player_object.name + " needs to enter the password to get access to commands!", color='db500a')


actions_lobby.append(("isequal", "set up lobby warning perimeter", set_up_lobby_warning_perimeter, "(self)", "lobby"))


def remove_lobby(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            self.bot.locations.remove('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "no lobby found oO", color='db500a')
            return False
    else:
        self.tn.send_message_to_player(player_object, player_object.name + " needs to enter the password to get access to commands!", color='db500a')


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self)", "lobby"))


def on_player_join(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is not True:
        try:
            # noinspection PyUnusedLocal
            location_dict = self.bot.locations.get('system', "lobby")
            self.tn.send_message_to_player(player_object, "yo ass will be deported to our lobby plus tha command-shit is restricted yo")
        except KeyError:
            return False


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self)", "lobby"))


def password(self, command):
    try:
        location_object = self.bot.locations.get('system', "lobby")
    except KeyError:
        return False

    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            try:
                location_object = self.bot.locations.get(player_object.steamid, 'spawn')
                self.tn.send_message_to_player(player_object, "You have been ported back to your original spawn!", color='22c927')
                self.tn.teleportplayer(player_object, location_object)
            except KeyError:
                self.tn.send_message_to_player(player_object, "I am terribly sorry, I seem to have misplaced your spawn, {}".format(player_object.name), color='db500a')
                return False


actions_lobby.append(("startswith", "password", password, "(self, command)", "lobby"))


def set_up_lobby_area(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        p = re.search(r"set up the lobby as a room starting from south west going north (.+) and east (.+) and up (.+)", command)
        if p:
            length = p.group(1)
            width = p.group(2)
            height = p.group(3)
            try:
                location_object = self.bot.locations.get('system', 'lobby')
            except KeyError:
                self.tn.send_message_to_player(player_object, "I can not find a location called {}".format('lobby'), color='db500a')
                return False

            set_width, allowed_range = location_object.set_width(width)
            set_length, allowed_range = location_object.set_length(length)
            set_height, allowed_range = location_object.set_height(height)
            if set_width is True and set_length is True and set_height is True:
                location_object.set_shape("room")
                location_object.set_center(player_object, location_object.width, location_object.length, location_object.height)
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the location {} ends here and spans {} meters ^^".format('lobby', int(location_object.radius * 2)), color='22c927')
            else:
                self.tn.send_message_to_player(player_object, "you given coordinates seem to be invalid", color='db500a')

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_lobby.append(("startswith", "set up the lobby", set_up_lobby_area, "(self, command)", "lobby"))


def set_up_lobby_teleport(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        p = re.search(r"set up teleport for lobby", command)
        if p:
            try:
                location_object = self.bot.locations.get('system', 'lobby')
            except KeyError:
                self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the lobby first!")
                return False

            if location_object.set_teleport_coordinates(player_object):
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "the teleport for {} has been set up!".format('lobby'), color='22c927')
            else:
                self.tn.send_message_to_player(player_object, "your position seems to be outside of the location", color='db500a')

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to commands!".format(player_object.name), color='db500a')


actions_lobby.append(("startswith", "set up teleport for lobby", set_up_lobby_teleport, "(self, command)", "lobby"))


"""
here come the observers
"""
observers_lobby = []


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self):
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
                self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>")


observers_lobby.append(("monitor", "player left lobby", player_is_outside_boundary, "(self)"))
