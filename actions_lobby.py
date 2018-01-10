import math
import re
import time
from location import Location

actions_lobby = []


def set_up_lobby(self, player_object, locations):
    if player_object.authenticated:
        location_dict = dict(
            owner=None,
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='sphere',
            radius=12,
            region=player_object.region
        )
        locations.update({'lobby': Location(**location_dict)})
        self.tn.say(player_object.name + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        self.tn.say(player_object.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, player_object, locations)"))


def set_up_lobby_perimeter(self, player_object, locations):
    if player_object.authenticated:
        try:
            location = locations['lobby']
        except KeyError:
            self.tn.say("you need to set up a lobby first silly: /set up lobby")
            return False

        radius = float(
            math.sqrt(
                (float(location.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(location.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(location.pos_z) - float(player_object.pos_z)) ** 2)
        )
        location.radius = radius
        locations.update({"lobby": location})
        self.tn.say("the lobby ends here and spawns " + str(int(radius * 2)) + " meters :)")
    else:
        self.tn.say(player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, player_object, locations)"))


def remove_lobby(self, player_object, locations):
    if player_object.authenticated:
        try:
            del locations['lobby']
        except KeyError:
            self.tn.say(" no lobby found oO")
            return False
    else:
        self.tn.say(player_object.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self, player_object, locations)"))


def on_player_join(self, player_object, locations):
    if not player_object.authenticated:
        try:
            location = locations["lobby"]
            self.tn.say("yo ass will be deported to our lobby plus tha command-shit is restricted yo")
        except KeyError:
            return False


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, player_object, locations)"))


def password(self, player_object, locations, command):
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            try:
                location = locations[player_object]['spawn']
                self.tn.teleportplayer(player_object, location)
            except KeyError:
                self.tn.say("i'm terribly sorry, i seem to have misplaced your spawn, " + player_object.name)
                return False


actions_lobby.append(("startswith", "password", password, "(self, player_object, locations, command)"))

"""
here come the observers
"""
observers_lobby = []


def player_left_area(self, player_object, locations):
    try:
        location = locations["lobby"]
    except KeyError:
        return False

    if not player_object.authenticated:
        distance_to_lobby_center = float(math.sqrt(
                (float(location.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(location.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(location.pos_z) - float(player_object.pos_z)) ** 2))

        if distance_to_lobby_center > location.radius:
            self.tn.teleportplayer(player_object, location)
            self.tn.say("You have been ported to the lobby! Authenticate with /password <password>")
            time.sleep(2)  # possibly not the best way to avoid mutliple teleports


observers_lobby.append(("player left lobby", player_left_area, "(self, player_object, locations)"))


def player_approaching_boundary_from_inside(self, player_object, locations):
    try:
        location = locations["lobby"]
    except KeyError:
        return False

    if not player_object.authenticated:
        distance_to_lobby_center=float(math.sqrt(
            (float(location.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(location.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(location.pos_z) - float(player_object.pos_z)) ** 2))

        if distance_to_lobby_center >= (location.radius * 0.75) and distance_to_lobby_center <= location.radius:
            self.tn.say("get your behind back in the lobby or else (" + str(abs(distance_to_lobby_center)) + ")")


observers_lobby.append(("player approaching boundary from inside", player_approaching_boundary_from_inside, "(self, player_object ,locations)"))
