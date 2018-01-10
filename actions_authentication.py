import re
from location import Location

actions_authentication = []


def password(self, player_object, command):
    p = re.search(r"password (.+)", command)
    if p:
        pwd = p.group(1)
        if pwd == "openup":
            if player_object.authenticated:
                self.tn.say(player_object.name + ", we trust you already <3")
            else:
                self.tn.say(player_object.name + " joined the ranks of literate people. Welcome!")
                player_object.authenticated = True
        else:
            player_object.authenticated = False
            self.tn.say(player_object.name + " has entered a wrong password oO!")


actions_authentication.append(("startswith", "password", password, "(self, player_object, command)"))


def on_player_join(self, player_object, locations):
    try:
        location = locations[player_object.name]['spawn']
        self.tn.say("Welcome back " + player_object.name + " o/")
    except KeyError:
        self.tn.say("this servers bot says Hi to " + player_object.name + " o/")
        location_dict = dict(
            name='spawn',
            owner=player_object.name,
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='point',
            radius=None,
            region=player_object.region
        )
        locations.update({player_object.name: {'spawn': Location(**location_dict)}})

    if not player_object.authenticated:
        self.tn.say("read the rules on https://chrani.net/rules")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self, player_object, locations)"))


