import math
import re
import time
from location import Location

actions_lobby = []


def set_up_lobby(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        location_dict = dict(
            owner='system',
            name='lobby',
            description='The \"there\'s no escape\" Lobby',
            messages_dict={
                "leaving_core": "leaving the lobby, you better be authenticated!!",
                "leaving_boundary": None,
                "entering_boundary": None,
                "entering_core": None
            },
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='sphere',
            radius=12,
            boundary_percentage=33,
            region=[player_object.region]
        )
        locations.add(Location(**location_dict), save=True)
        self.tn.send_message_to_player(player_object, player_object.name + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        self.tn.send_message_to_player(player_object, player_object.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, players, locations)"))


def set_up_lobby_perimeter(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        try:
            location_object = locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby")
            return False

        if location_object.set_radius(player_object):
            locations.add(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The Lobby ends here and spawns {} meters ^^".format(int(location_object.radius * 2)))
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)))
    else:
        self.tn.say(player_object, player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, players, locations)"))


def remove_lobby(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
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
    if not player_object.authenticated:
        try:
            location_dict = locations.get('system', "lobby")
            self.tn.send_message_to_player(player_object, "yo ass will be deported to our lobby plus tha command-shit is restricted yo")
        except KeyError:
            return False


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, players, locations)"))


def password(self, players, locations, command):
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
            time.sleep(2)  # possibly not the best way to avoid mutliple teleports in a row


observers_lobby.append(("player left lobby", player_is_outside_boundary, "(self, players, locations)"))
