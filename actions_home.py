import math
from location import Location

actions_home = []


def make_this_my_home(self, player_object, locations):
    if player_object.authenticated:
        location_dict = dict(
            owner=player_object.name,
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='sphere',
            radius=12,
            region=player_object.region
        )
        try:
            locations[player_object.name].update({'home': Location(**location_dict)})
        except:
            locations[player_object.name] = {'home': Location(**location_dict)}

        self.tn.say(player_object.name + " has decided to settle down!")
    else:
        self.tn.say(player_object.name + " is no authorized no nope. should go read read!")


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, player_object, locations)"))


def take_me_home(self, player_object, locations):
    if player_object.authenticated:
        try:
            location_object = locations[player_object.name]["home"]
            self.tn.teleportplayer(player_object, location_object)
            self.tn.say(player_object.name + " got homesick")
            return True
        except KeyError:
            self.tn.say(player_object.name + " is apparently homeless...")
    else:
        self.tn.say(player_object.name + " needs to enter the password to get access to sweet commands!")


actions_home.append(("isequal", "take me home", take_me_home, "(self, player_object, locations)"))


def set_up_home_perimeter(self, player_object, locations):
    if player_object.authenticated:
        try:
            location_object = locations[player_object.name]["home"]
        except KeyError:
            self.tn.say("coming from the wrong end... set up a home first!")
            return False

        radius = float(
            math.sqrt(
                (float(location_object.pos_x) - float(player_object.pos_x)) ** 2 + (float(location_object.pos_y) - float(player_object.pos_y)) ** 2 + (float(location_object.pos_z) - float(player_object.pos_z)) ** 2)
            )
        location_object.radius = radius

        self.tn.say("your estate ends here and spawns " + str(int(radius * 2)) + " meters ^^")
    else:
        self.tn.say(player_object.name + " needs to enter the password to get access to commands!")


actions_home.append(("isequal", "my estate ends here", set_up_home_perimeter, "(self, player_object, locations)"))

