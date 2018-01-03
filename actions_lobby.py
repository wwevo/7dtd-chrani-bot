import math
import re

actions_lobby = []


def set_up_lobby(self, player, locations):
    if "authenticated" in player and player["authenticated"]:
        if "lobby" in locations:
            location = locations["lobby"]
        else:
            location = {}
            locations.update({"lobby": location})

        location.update({"pos_x": player["pos_x"]})
        location.update({"pos_y": player["pos_y"]})
        location.update({"pos_z": player["pos_z"]})
        location.update({"radius": 10})
        
        locations.update({"lobby": location})

        self.tn.say(player["name"] + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        self.tn.say(player["name"] + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, player, locations)"))


def set_up_lobby_perimeter(self, player, locations):
    if "authenticated" in player and player["authenticated"]:
        if "lobby" in locations:
            location = locations["lobby"]
        else:
            self.tn.say("you need to set a lobby up first silly: /set up lobby")
            return False

        radius = float(
            math.sqrt(
                (float(location["pos_x"]) - float(player["pos_x"])) ** 2 + (float(location["pos_y"]) - float(player["pos_y"])) ** 2 + (float(location["pos_z"]) - float(player["pos_z"])) ** 2)
            )
        location.update({"radius": radius})
        locations.update({"lobby": location})

        self.tn.say("lobby ends here and spawns " + str(int(radius * 2)) + " meters :)")
    else:
        self.tn.say(player["name"] + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, player, locations)"))


def remove_lobby(self, player, locations):
    if "authenticated" in player and player["authenticated"]:
        if "lobby" in locations:
            del locations["lobby"]
        else:
            self.tn.say(" no loby found oO")
    else:
        self.tn.say(player["name"] + " needs to enter the password to get access to commands!")


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self, player, locations)"))


def on_player_join(self, player, locations):
    if "authenticated" not in player or not player["authenticated"]:
        if "lobby" in locations:
            location = locations["lobby"]
            self.tn.say("yo ass will be ported to our lobby plus tha command-shit is restricted yo")
            self.tn.say("read the rules on https://chrani.net/rules")
            self.tn.say("enter the password with /password <password> in this chat")
            self.tn.teleport_player(player, location)
        else:
            self.tn.say("your account is restricted until you have read the rules")
            self.tn.say("read the rules on https://chrani.net/rules")
            self.tn.say("enter the password with /password <password> in this chat")


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, player, locations)"))


def on_respawn_after_death(self, player, locations):
    """
    sends players who are not authenticated back to the lobby
    :param self: needed for the class it will be running in
    :param player: player-object pulled from database
    :param connection: Telnet command object
    :return: nothing to return
    """
    if "authenticated" in player and not player["authenticated"]:
        if "lobby" in locations:
            location = locations["lobby"]
            self.tn.teleportplayer(player, location)
            self.tn.say("there is no escape from the lobby!")


actions_lobby.append(("isequal", "Died", on_respawn_after_death, "(self, player, locations)"))


def password(self, player, command, locations):
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            # print "correct password!!"
            if not player["authenticated"]:
                if "spawn" in player:
                    location = player["spawn"]
                    self.tn.teleport_player(player, location)
                    del player["spawn"]
                else:
                    self.tn.say(player["name"] + " could not find your place of birth!")


actions_lobby.append(("startswith", "password", password, "(self, player, command, locations)"))

"""
here come the observers
"""
observers_lobby = []


def player_left_area(self, player, locations):
    if "lobby" in locations:
        location = locations["lobby"]
    else:
        return

    if "authenticated" in player and not player["authenticated"]:
        distance_to_lobby_center = float(math.sqrt(
                (float(location["pos_x"]) - float(player["pos_x"])) ** 2 + (
                    float(location["pos_y"]) - float(player["pos_y"])) ** 2 + (
                    float(location["pos_z"]) - float(player["pos_z"])) ** 2))

        if distance_to_lobby_center > location["radius"]:
            self.tn.say("And stay there!")
            self.tn.teleportplayer(player, location)


observers_lobby.append(("player left lobby", player_left_area, "(self, player, locations)"))


def player_approaching_boundary_from_inside(self, player, locations):
    if "lobby" in locations:
        location = locations["lobby"]
    else:
        return

    if "authenticated" in player and not player["authenticated"]:
        distance_to_lobby_center = float(math.sqrt(
                (float(location["pos_x"]) - float(player["pos_x"])) ** 2 + (
                    float(location["pos_y"]) - float(player["pos_y"])) ** 2 + (
                    float(location["pos_z"]) - float(player["pos_z"])) ** 2))

        if distance_to_lobby_center >= (location["radius"] / 2) and distance_to_lobby_center <= location["radius"]:
            self.tn.say("get your ass back in the lobby or else (" + str(abs(distance_to_lobby_center)) + ")")


observers_lobby.append(("player approaching boundary from inside", player_approaching_boundary_from_inside, "(self, player,locations)"))
