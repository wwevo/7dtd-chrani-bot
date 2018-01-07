actions_status_messages = []


def on_player_join(self, player):
    self.tn.say("Welcome " + player.name + " o/")


actions_status_messages.append(("isequal", "JoinMultiplayer", on_player_join, "(self, player)"))


def on_player_death(self, player):
    self.tn.say(player.name + " is no more. pity.")


actions_status_messages.append(("isequal", "died", on_player_death, "(self, player)"))


def on_respawn_after_death(self, player):
    self.tn.say(player.name + " is Bjorn again! No. Is " + player.name + " again! MAGIC!!")


actions_status_messages.append(("isequal", "Died", on_respawn_after_death, "(self, player)"))

