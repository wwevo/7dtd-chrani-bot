import re

actions_authentication = []


def password(self, player, command):
    p = re.search(r"password (.+)", command)
    if p:
        pwd = p.group(1)
        if pwd == "openup":
            if "authenticated" in player and player["authenticated"]:
                self.tn.say(player["name"] + ", we trust you already <3")
            else:
                self.tn.say(player["name"] + " joined the ranks of literate people. Welcome!")
                player.update({"authenticated": True})
        else:
            player.update({"authenticated": False})
            self.tn.say(player["name"] + " has entered a wrong password oO!")


actions_authentication.append(("startswith", "password", password, "(self, player, command)"))


def on_player_join(self, player, locations):
    if "authenticated" not in player or not player["authenticated"]:
        self.tn.say("read the rules on https://chrani.net/rules")
        self.tn.say("enter the password with /password <password> in this chat")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self, player, locations)"))


