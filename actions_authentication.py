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
    if "spawn" in locations:
        self.tn.say("Welcome back " + player.name + " o/")
    else:
        location = {}
        location["pos_x"] = player.pos_x
        location["pos_y"] = player.pos_y
        location["pos_z"] = player.pos_z
        # player.update({"spawn": location})

        self.tn.say("this servers bot says Hi to " + player.name + " o/")
    if player.authenticated:
        self.tn.say("read the rules on https://chrani.net/rules")
        self.tn.say("enter the password with /password <password> in this chat")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self, player, locations)"))


