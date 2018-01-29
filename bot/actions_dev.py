actions_dev = []


def fix_players_legs(self, player_object):
    self.tn.debuffplayer(player_object, "brokenLeg")
    self.tn.debuffplayer(player_object, "sprainedLeg")
    self.tn.send_message_to_player(player_object, "your legs have been taken care of ^^")


actions_dev.append(("isequal", "fix my legs please", fix_players_legs, "(self, player_object)"))


def stop_the_bleeding(self, player_object):
    self.tn.debuffplayer(player_object, "bleeding")
    self.tn.send_message_to_player(player_object, "your wounds have been bandaided ^^")


actions_dev.append(("isequal", "make me stop leaking", stop_the_bleeding, "(self, player_object)"))


def apply_first_aid(self, player_object):
    self.tn.buffplayer(player_object, "firstAidLarge")
    self.tn.send_message_to_player(player_object, "feel the power flowing through you!! ^^")


actions_dev.append(("isequal", "heal me up scotty", apply_first_aid, "(self, player_object)"))


def make_player_admin(self, player_object):
    self.tn.set_admin_level(player_object, "2")
    self.tn.send_message_to_player(player_object, "and He said 'Let there be unlimited POWER!'. hit F1 and type cm <enter>, dm <enter>. exit console. press 'q' to fly, 'u' for items.")


actions_dev.append(("isequal", "make me all powerful!", make_player_admin, "(self, player_object)"))
