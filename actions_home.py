import math
import re
from location import Location

actions_home = []


def make_this_my_home(self, player_object, locations):
    if player_object.authenticated:
        location_dict = dict(
            name='home',
            owner=player_object.name,
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='sphere',
            radius=12,
            boundary_percentage=33,
            region=[player_object.region]
        )
        try:
            locations[player_object.steamid].update({'home': Location(**location_dict)})
        except:
            locations[player_object.steamid] = {'home': Location(**location_dict)}

        self.tn.say("{} has decided to settle down!".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, player_object, locations)"))


def name_my_home(self, player_object, locations, command):
    print "command issued : " + command
    p = re.search(r"i call my home (.+)", command)
    if p:
        description = p.group(1)
        if player_object.authenticated:
            try:
                location_object = locations[player_object.steamid]["home"]
                location_object.description = description
                print description
                self.tn.say("{} called their home {}".format(player_object.name, location_object.description))
                return True

            except KeyError:
                self.tn.send_message_to_player(player_object, "{} can't name which you don't have!!".format(player_object.name))
        else:
            self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_home.append(("startswith", "i call my home", name_my_home, "(self, player_object, locations, command)"))


def take_me_home(self, player_object, locations):
    if player_object.authenticated:
        try:
            location_object = locations[player_object.steamid]["home"]
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
            location_object = locations[player_object.steamid]["home"]
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
        for owner, player_locations_dict in locations.iteritems():
            if "home" in player_locations_dict:
                if player_locations_dict["home"].player_crossed_outside_boundary_from_outside(player_object):
                    self.tn.send_message_to_player(player_object, "you have entered the lands of {}".format(player_locations_dict["home"].owner))
    except TypeError:
        pass


observers_home.append(("player crossed home boundary from outside", player_crossed_outside_boundary_from_outside, "(self, player_object, locations)"))


def player_crossed_outside_boundary_from_inside(self, player_object, locations):
    try:
        for owner, player_locations_dict in locations.iteritems():
            if "home" in player_locations_dict:
                if player_locations_dict["home"].player_crossed_outside_boundary_from_inside(player_object):
                    self.tn.send_message_to_player(player_object, "you have left the lands of {}".format(player_locations_dict["home"].owner))
    except TypeError:
        pass


observers_home.append(("player crossed home boundary from inside", player_crossed_outside_boundary_from_inside, "(self, player_object, locations)"))


def player_crossed_inside_core_from_boundary(self, player_object, locations):
    try:
        for owner, player_locations_dict in locations.iteritems():
            if "home" in player_locations_dict:
                if player_locations_dict["home"].player_crossed_inside_core_from_boundary(player_object):
                    self.tn.send_message_to_player(player_object, "you have entered {}'s private-area: {}".format(player_locations_dict["home"].owner, player_locations_dict["home"].description))
    except TypeError:
        pass


observers_home.append(("player crossed home-core boundary from outside", player_crossed_inside_core_from_boundary, "(self, player_object, locations)"))


def player_crossed_inside_boundary_from_core(self, player_object, locations):
    try:
        for owner, player_locations_dict in locations.iteritems():
            if "home" in player_locations_dict:
                if player_locations_dict["home"].player_crossed_inside_boundary_from_core(player_object):
                    self.tn.send_message_to_player(player_object, "you have left {}'s private-area: {}".format(player_locations_dict["home"].owner, player_locations_dict["home"].description))
    except TypeError:
        pass


observers_home.append(("player crossed home-core boundary from inside", player_crossed_inside_boundary_from_core, "(self, player_object, locations)"))