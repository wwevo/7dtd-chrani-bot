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
                location = locations[player_object.name]['spawn']
                self.tn.teleportplayer(player_object, location)
            except KeyError:
                self.tn.say("i'm terribly sorry, i seem to have misplaced your spawn, " + player_object.name)
                return False


actions_lobby.append(("startswith", "password", password, "(self, player_object, locations, command)"))

"""
here come the observers
"""
observers_lobby = []


def player_is_outside_boundary(self, player_object, locations):
    try:
        location = locations["lobby"]
    except KeyError:
        return False

    if not player_object.authenticated and player_object.is_responsive:
        if location.player_is_outside_boundary(player_object):
            if self.tn.teleportplayer(player_object, location):
                self.tn.say("You have been ported to the lobby! Authenticate with /password <password>")
            # time.sleep(2)  # possibly not the best way to avoid mutliple teleports in a row


observers_lobby.append(("player left lobby", player_is_outside_boundary, "(self, player_object, locations)"))


def player_is_near_boundary_inside(self, player_object, locations):
    try:
        location = locations["lobby"]
    except KeyError:
        return False

    if not player_object.authenticated:
        if location.player_is_near_boundary_inside(player_object):
            # TODO: this needs to be a sheduled message on a set timer. like every second, every two seconds.
            #       we will also need that to remind people if they are in a reset zone or otherwise noteworthy location
            #       player is in location -> start message
            #       player is in boundary -> increase frequency and or clolor?
            #       player left location -> end message
            #           thought about it... locations should have their own triggers which can be polled here
            #           so it could look like
            #               if player_object is location_object.near:
            #               if player_object is location_object.entering:
            #               if player_object is location_object.inside_boundary:
            #               if player_object is location_object.inside_core:
            #           all regions affected by the location should be stored and then compared to the players current
            #           region
            self.tn.say("get your behind back in the lobby or we'll manhandle you there rudely!")


observers_lobby.append(("player approaching boundary from inside", player_is_near_boundary_inside, "(self, player_object ,locations)"))


def player_is_near_boundary_outside(self, player_object, locations):
    try:
        location = locations["lobby"]
    except KeyError:
        return False

    if location.player_is_near_boundary_outside(player_object):
        self.tn.say("you are near the lobby, there might be triggered actions. beware!")


observers_lobby.append(("player approaching boundary from outside", player_is_near_boundary_outside, "(self, player_object ,locations)"))
