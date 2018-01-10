import math
import re
import time

actions_lobby = []


def set_up_lobby(self, player, locations):
    if player.authenticated:
        locations.update({
            'lobby': {'pos_x': int(player.pos_x), 'pos_y': int(player.pos_y),
                                   'pos_z': int(player.pos_z), 'shape': 'sphere', 'radius': 10,
                                   'region': player.region}
                          })
        self.tn.say(player.name + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        self.tn.say(player.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, player, locations)"))


def set_up_lobby_perimeter(self, player, locations):
    if player.authenticated:
        if "lobby" in locations:
            location = locations["lobby"]
        else:
            self.tn.say("you need to set a lobby up first silly: /set up lobby")
            return False

        radius = float(
            math.sqrt(
                (float(location["pos_x"]) - float(player.pos_x)) ** 2 + (float(location["pos_y"]) - float(player.pos_y)) ** 2 + (float(location["pos_z"]) - float(player.pos_z)) ** 2)
            )
        location.update({"radius": radius})
        locations.update({"lobby": location})

        self.tn.say("lobby ends here and spawns " + str(int(radius * 2)) + " meters :)")
    else:
        self.tn.say(player.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, player, locations)"))


def remove_lobby(self, player, locations):
    if player.authenticated:
        if "lobby" in locations:
            del locations["lobby"]
        else:
            self.tn.say(" no loby found oO")
    else:
        self.tn.say(player.name + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self, player, locations)"))


def on_player_join(self, player, locations):
    if not player.authenticated:
        if "lobby" in locations:
            location = locations["lobby"]
            self.tn.say("yo ass will be deported to our lobby plus tha command-shit is restricted yo")


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, player, locations)"))


def password(self, player, locations, command):
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            if player.name in locations:
                if "spawn" in locations[player.name]:
                    location = locations[player.name]["spawn"]
                    self.tn.teleportplayer(player, location)


actions_lobby.append(("startswith", "password", password, "(self, player, locations, command)"))

"""
here come the observers
"""
observers_lobby = []


def player_left_area(self, player, locations):
    if "lobby" in locations:
        location = locations["lobby"]
    else:
        return

    if not player.authenticated:
        distance_to_lobby_center = float(math.sqrt(
                (float(location["pos_x"]) - float(player.pos_x)) ** 2 + (
                    float(location["pos_y"]) - float(player.pos_y)) ** 2 + (
                    float(location["pos_z"]) - float(player.pos_z)) ** 2))

        if distance_to_lobby_center > location["radius"]:
            self.tn.teleportplayer(player, location)
            self.tn.say("You have been ported to the lobby! Authenticate with /password <password>")
            time.sleep(3)

observers_lobby.append(("player left lobby", player_left_area, "(self, player, locations)"))


def player_approaching_boundary_from_inside(self, player, locations):
    if "lobby" in locations:
        location = locations["lobby"]
    else:
        return

    if not player.authenticated:
        distance_to_lobby_center = float(math.sqrt(
                (float(location["pos_x"]) - float(player.pos_x)) ** 2 + (
                    float(location["pos_y"]) - float(player.pos_y)) ** 2 + (
                    float(location["pos_z"]) - float(player.pos_z)) ** 2))

        if distance_to_lobby_center >= (location["radius"] * 0.75) and distance_to_lobby_center <= location["radius"]:
            self.tn.say("get your behind back in the lobby or else (" + str(abs(distance_to_lobby_center)) + ")")


observers_lobby.append(("player approaching boundary from inside", player_approaching_boundary_from_inside, "(self, player,locations)"))
