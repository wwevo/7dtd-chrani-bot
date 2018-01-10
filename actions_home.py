actions_home = []


def make_this_my_home(self, player, locations):
    if player.authenticated:
        locations.update({
            player.name: {'home': {'owner': player.name, 'pos_x': int(player.pos_x), 'pos_y': int(player.pos_y),
                     'pos_z': int(player.pos_z), 'shape': 'sphere', 'radius': 12, 'region': player.region}
        }})
        self.tn.say(player.name + " has decided to settle down!")
    else:
        self.tn.say(player.name + " id no authorized no nope. should go read read!")


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, player, locations)"))


def take_me_home(self, player, locations):
    if player.authenticated:
        if player.name in locations:
            if "home" in locations[player.name]:
                location = locations[player.name]["home"]
                self.tn.teleportplayer(player, location)
                self.tn.say(player.name + " got homesick")
                return True
        self.tn.say(player.name + " is apparently homeless...")
    else:
        self.tn.say(player.name + " needs to enter the password to get access to sweet commands!")


actions_home.append(("isequal", "take me home", take_me_home, "(self, player, locations)"))
