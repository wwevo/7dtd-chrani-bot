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
            region=[player_object.region]
        )
        try:
            locations[player_object.name].update({'home': Location(**location_dict)})
        except:
            locations[player_object.name] = {'home': Location(**location_dict)}

        self.tn.say("{} has decided to settle down!".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, player_object, locations)"))


def take_me_home(self, player_object, locations):
    if player_object.authenticated:
        try:
            location_object = locations[player_object.name]["home"]
            self.tn.teleportplayer(player_object, location_object)
            self.tn.say("{} got homesick".format(player_object.name))
            return True
        except KeyError:
            self.tn.send_message_to_player(player_object, "{} is apparently homeless...".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_home.append(("isequal", "take me home", take_me_home, "(self, player_object, locations)"))


def set_up_home_perimeter(self, player_object, locations):
    if player_object.authenticated:
        try:
            location_object = locations[player_object.name]["home"]
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!")
            return False

        radius = float(
            math.sqrt(
                (float(location_object.pos_x) - float(player_object.pos_x)) ** 2 + (float(location_object.pos_y) - float(player_object.pos_y)) ** 2 + (float(location_object.pos_z) - float(player_object.pos_z)) ** 2)
            )
        location_object.radius = radius

        self.tn.send_message_to_player(player_object, "your estate ends here and spawns {} meters ^^".format(int(radius * 2)))
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to commands!".format(player_object.name))


actions_home.append(("isequal", "my estate ends here", set_up_home_perimeter, "(self, player_object, locations)"))

"""
here come the observers
"""
observers_home = []


def player_crossed_outside_boundary_from_outside(self, player_object, locations):
    try:
        for owner, location_object in locations.iteritems():
            if "home" in location_object:
                if location_object["home"].player_crossed_outside_boundary_from_outside(player_object):
                    self.tn.send_message_to_player(player_object, "you have entered the lands of {}".format(location_object["home"].owner))
    except TypeError:
        pass


observers_home.append(("player crossed home boundary from outside", player_crossed_outside_boundary_from_outside, "(self, player_object, locations)"))


def player_crossed_outside_boundary_from_inside(self, player_object, locations):
    try:
        for owner, location_object in locations.iteritems():
            if "home" in location_object:
                if location_object["home"].player_crossed_outside_boundary_from_inside(player_object):
                    self.tn.send_message_to_player(player_object, "you have left the lands of {}".format(location_object["home"].owner))
    except TypeError:
        pass


observers_home.append(("player crossed home boundary from inside", player_crossed_outside_boundary_from_inside, "(self, player_object, locations)"))


def player_crossed_inside_core_from_boundary(self, player_object, locations):
    try:
        for owner, location_object in locations.iteritems():
            if "home" in location_object:
                if location_object["home"].player_crossed_inside_core_from_boundary(player_object):
                    self.tn.send_message_to_player(player_object, "you have entered {}'s core".format(location_object["home"].name))
    except TypeError:
        pass


observers_home.append(("player crossed home-core boundary from outside", player_crossed_inside_core_from_boundary, "(self, player_object, locations)"))


def player_crossed_inside_boundary_from_core(self, player_object, locations):
    try:
        for owner, location_object in locations.iteritems():
            if "home" in location_object:
                if location_object["home"].player_crossed_inside_boundary_from_core(player_object):
                    self.tn.send_message_to_player(player_object, "you have left {}'s core".format(location_object["home"].name))
    except TypeError:
        pass


observers_home.append(("player crossed home-core boundary from inside", player_crossed_inside_boundary_from_core, "(self, player_object, locations)"))