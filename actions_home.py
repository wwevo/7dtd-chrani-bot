actions_home = []


def make_this_my_home(self, player):
    if "authenticated" in player and player["authenticated"]:
        location = {}
        location["pos_x"] = player.pos_x
        location["pos_y"] = player.pos_y
        location["pos_z"] = player.pos_z
        # player.update({"home": location})

        self.tn.say(player.name + " has decided to settle down!")
    else:
        self.tn.say(player.name + " id no authorized no nope. should go read read!")


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, player)"))


def take_me_home(self, player):
    if player.authenticated:
        pass
        # if "home" in player:
        #     location = player.home
        #     self.tn.teleportplayer(player, location)
        #     self.tn.say(player.name + " got homesick")
        # else:
        #     self.tn.say(player.name + " is apparently homeless...")
    else:
        self.tn.say(player.name + " needs to enter the password to get access to sweet commands!")


actions_home.append(("isequal", "take me home", take_me_home, "(self, player)"))
