import math
import re
import time
from location import Location

actions_lobby = []


def set_up_lobby(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated is True:
        """ full dictionary setup. These settings can all be set individually on a set_{option} basis
        """
        location_dict = dict(
            owner='system',
            name='The Lobby',
            identifier='lobby',
            description='The \"there is no escape\" Lobby',
            messages_dict={
                "leaving_core": None,
                "leaving_boundary": "leaving the lobby, you better be authenticated!!",
                "entering_boundary": "entering the lobby, Why?",
                "entering_core": None
            },
            shape='sphere',
            radius=12,
            warning_boundary=8,
            region=[player_object.region],
            list_of_players_inside=[player_object.steamid]
        )
        location_object = Location(**location_dict)
        location_object.set_coordinates(player_object)
        locations.upsert(location_object, save=True)
        self.tn.send_message_to_player(player_object, player_object.name + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        self.tn.send_message_to_player(player_object, player_object.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, players, locations)"))


def set_up_lobby_perimeter(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            location_object = locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby")
            return False

        if location_object.set_radius(player_object):
            locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)))
        else:
            self.tn.send_message_to_player(player_object, "Your given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)))
    else:
        self.tn.say(player_object, player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, players, locations)"))


def set_up_lobby_warning_perimeter(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            location_object = locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby")
            return False

        if location_object.set_warning_boundary(player_object):
            locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby-warnings will be issued from this point on")
        else:
            self.tn.send_message_to_player(player_object, "Is this inside the lobby perimeter?")
    else:
        self.tn.say(player_object, player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby warning perimeter", set_up_lobby_warning_perimeter, "(self, players, locations)"))


def remove_lobby(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            locations.remove('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "no lobby found oO")
            return False
    else:
        self.tn.send_message_to_player(player_object, player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self, players, locations)"))


def on_player_join(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated is not True:
        try:
            location_dict = locations.get('system', "lobby")
            self.tn.send_message_to_player(player_object, "yo ass will be deported to our lobby plus tha command-shit is restricted yo")
        except KeyError:
            return False


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, players, locations)"))


def password(self, players, locations, command):
    try:
        location_dict = locations.get('system', "lobby")
    except KeyError:
        return False

    player_object = players.get(self.player_steamid)
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            try:
                location = locations.get(player_object.steamid, 'spawn')
                self.tn.send_message_to_player(player_object, "You have been ported back to your original spawn!")
                self.tn.teleportplayer(player_object, location)
            except KeyError:
                self.tn.send_message_to_player(player_object, "i'm terribly sorry, i seem to have misplaced your spawn, " + player_object.name)
                return False


actions_lobby.append(("startswith", "password", password, "(self, players, locations, command)"))

"""
here come the observers
"""
observers_lobby = []


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self, players, locations):
    player_object = players.get(self.player_steamid)
    try:
        location_object = locations.get('system', "lobby")
    except KeyError:
        return False

    if player_object.authenticated is not True and player_object.is_responsive:
        if not location_object.player_is_inside_boundary(player_object):
            if self.tn.teleportplayer(player_object, location_object):
                self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>")


observers_lobby.append(("player left lobby", player_is_outside_boundary, "(self, players, locations)"))
