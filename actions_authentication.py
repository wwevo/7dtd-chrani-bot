import re

actions_authentication = []


def password(self, player, command):
    p = re.search(r"password (.+)", command)
    if p:
        pwd = p.group(1)
        if pwd == "openup":
            if player.authenticated:
                self.tn.say(player.name + ", we trust you already <3")
            else:
                self.tn.say(player.name + " joined the ranks of literate people. Welcome!")
                player.authenticated = True
        else:
            player.authenticated = False
            self.tn.say(player.name + " has entered a wrong password oO!")


actions_authentication.append(("startswith", "password", password, "(self, player, command)"))


def on_player_join(self, player, locations):
    if player.name in locations:
        if "spawn" in locations[player.name]:
            self.tn.say("Welcome back " + player.name + " o/")
    else:
        locations.update({
            player.name: {'spawn': {'owner': player.name, 'pos_x': int(player.pos_x), 'pos_y': int(player.pos_y),
                     'pos_z': int(player.pos_z), 'shape': None, 'radius': None, 'region': player.region}
        }})

        self.tn.say("this servers bot says Hi to " + player.name + " o/")
    if not player.authenticated:
        self.tn.say("read the rules on https://chrani.net/rules")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self, player, locations)"))


