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