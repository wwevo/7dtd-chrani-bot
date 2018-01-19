import math
import re
from location import Location

actions_home = []


def make_this_my_home(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        location_dict = dict(
            name='home',
            owner=player_object.steamid,
            description=player_object.name + "\'s home",
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='sphere',
            radius=12,
            boundary_percentage=33,
            region=[player_object.region]
        )
        locations.add(Location(**location_dict))
        self.tn.say("{} has decided to settle down!".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_home.append(("isequal", "make this my home", make_this_my_home, "(self, players, locations)"))


def name_my_home(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    p = re.search(r"i call my home (.+)", command)
    if p:
        description = p.group(1)
        if player_object.authenticated:
            try:
                location_object = locations.get(player_object.steamid, "home")
                location_object.set_description(description)
                locations.add(location_object, save=True)
                self.tn.say("{} called their home {}".format(player_object.name, location_object.description))
                return True

            except KeyError:
                self.tn.send_message_to_player(player_object, "{} can't name which you don't have!!".format(player_object.name))
        else:
            self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_home.append(("startswith", "i call my home", name_my_home, "(self, players, locations, command)"))


def take_me_home(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        try:
            location_object = locations.get(player_object.steamid, "home")
            self.tn.teleportplayer(player_object, location_object)
            self.tn.say("{} got homesick".format(player_object.name))
            return True
        except KeyError:
            self.tn.send_message_to_player(player_object, "{} is apparently homeless...".format(player_object.name))
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_home.append(("isequal", "take me home", take_me_home, "(self, players, locations)"))


def set_up_home_perimeter(self, players, locations):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        try:
            location_object = locations.get(player_object.steamid, "home")
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!")
            return False

        radius = float(
            math.sqrt(
                (float(location_object.pos_x) - float(player_object.pos_x)) ** 2 + (float(location_object.pos_y) - float(player_object.pos_y)) ** 2 + (float(location_object.pos_z) - float(player_object.pos_z)) ** 2)
            )
        if location_object.set_radius(radius):
            locations.add(location_object, save=True)
            self.tn.send_message_to_player(player_object, "your estate ends here and spawns {} meters ^^".format(int(radius * 2)))
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(radius * 2)))

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to commands!".format(player_object.name))


actions_home.append(("isequal", "my estate ends here", set_up_home_perimeter, "(self, players, locations)"))


def make_my_home_a_shape(self, players, locations, command):
    player_object = players.get(self.player_steamid)
    p = re.search(r"make my home a (.+)", command)
    if p:
        shape = p.group(1)
        if player_object.authenticated:
            try:
                location_object = locations.get(player_object.steamid, "home")
                if location_object.set_shape(shape):
                    locations.add(location_object, save=True)
                    self.tn.send_message_to_player(player_object,"{}'s home is a {} now.".format(player_object.name, shape))
                    return True
                else:
                    self.tn.send_message_to_player(player_object,"{} is not an allowed shape at this time!".format(shape))
                    return False

            except KeyError:
                self.tn.send_message_to_player(player_object, "{} can not change that which you do not own!!".format(player_object.name))
        else:
            self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name))


actions_home.append(("startswith", "make my home a", make_my_home_a_shape, "(self, players, locations, command)"))


"""
here come the observers
"""
observers_home = []


def player_crossed_outside_boundary_from_outside(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, player_locations_dict in locations.locations_dict.iteritems():
        try:
            if player_locations_dict["home"].player_crossed_outside_boundary_from_outside(player_object):
                self.tn.send_message_to_player(player_object, "you have entered the lands of {}".format(player_locations_dict["home"].owner))
        except Exception:
            pass


observers_home.append(("player crossed home boundary from outside", player_crossed_outside_boundary_from_outside, "(self, players, locations)"))


def player_crossed_outside_boundary_from_inside(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, player_locations_dict in locations.locations_dict.iteritems():
        try:
            if player_locations_dict["home"].player_crossed_outside_boundary_from_inside(player_object):
                self.tn.send_message_to_player(player_object, "you have left the lands of {}".format(player_locations_dict["home"].owner))
        except Exception:
            pass


observers_home.append(("player crossed home boundary from inside", player_crossed_outside_boundary_from_inside, "(self, players, locations)"))


def player_crossed_inside_core_from_boundary(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, player_locations_dict in locations.locations_dict.iteritems():
        try:
            if player_locations_dict["home"].player_crossed_inside_core_from_boundary(player_object):
                self.tn.send_message_to_player(player_object, "you have entered {}'s private-area: {}".format(player_locations_dict["home"].owner, player_locations_dict["home"].description))
        except Exception:
            pass


observers_home.append(("player crossed home-core boundary from outside", player_crossed_inside_core_from_boundary, "(self, players, locations)"))


def player_crossed_inside_boundary_from_core(self, players, locations):
    player_object = players.get(self.player_steamid)
    for owner, player_locations_dict in locations.locations_dict.iteritems():
        try:
            if player_locations_dict["home"].player_crossed_inside_boundary_from_core(player_object):
                self.tn.send_message_to_player(player_object, "you have left {}'s private-area: {}".format(player_locations_dict["home"].owner, player_locations_dict["home"].description))
        except Exception:
            pass


observers_home.append(("player crossed home-core boundary from inside", player_crossed_inside_boundary_from_core, "(self, players, locations)"))