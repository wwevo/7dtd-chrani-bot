actions_welcome = []


def on_player_join(self, player):
    self.tn.say("Welcome " + player["name"] + " o/")


actions_welcome.append(("isequal", "joined the game", on_player_join, "(self, player)"))


def on_player_death(self, player):
    self.tn.say(player["name"] + " is no more. pity.")


actions_welcome.append(("isequal", "died", on_player_death, "(self, player)"))


def on_respawn_after_death(self, player):
    self.tn.say(player["name"] + " is Bjorn again! no. is " + player["name"] + " again! MAGIC!!")


actions_welcome.append(("isequal", "Died", on_respawn_after_death, "(self, player)"))

