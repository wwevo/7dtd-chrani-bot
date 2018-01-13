import math


class Location(object):
    owner = str
    name = str
    pos_x = float
    pos_y = float
    pos_z = float
    shape = str
    radius = float
    boundary_percentage = 33

    # Todo: region should be a list as a location nd it's effect can spawn several regions. capture all regions if empty
    region = list

    last_player_activity_dict = {}

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def player_is_inside_boundary(self, player_object):
        distance_to_location_center = 0
        if self.shape == "sphere":
            # Todo: i also want cube, room, country (bottom to top), maybe later polygon ^^
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
        player_is_inside_boundary = distance_to_location_center <= float(self.radius)

        # print "player_is_inside_boundary: {} of {}".format(player_is_inside_boundary, self.name)
        return player_is_inside_boundary

    def player_is_inside_core(self, player_object):
        distance_to_location_center = 0
        if self.shape == "sphere":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
        distance_to_core_boundary = (float(self.radius) / 100) * (100 - float(self.boundary_percentage))
        player_is_inside_core = distance_to_location_center <= distance_to_core_boundary

        # print "player_is_inside_core: {} of {}".format(player_is_inside_core, self.name)
        return player_is_inside_core

    def player_crossed_outside_boundary_from_outside(self, player_object):
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.name][self.name]["player_crossed_outside_boundary_from_outside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.name not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.name] = {}
        if self.name not in self.last_player_activity_dict[player_object.name]:
            self.last_player_activity_dict[player_object.name].update({self.name: {}})

        self.last_player_activity_dict[player_object.name][self.name].update({"player_crossed_outside_boundary_from_outside": player_is_inside_boundary})

        if player_was_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_is_inside_boundary:
                return True
            else:
                return False

    def player_crossed_outside_boundary_from_inside(self, player_object):
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.name][self.name]["player_crossed_outside_boundary_from_inside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.name not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.name] = {}
        elif self.name not in self.last_player_activity_dict[player_object.name]:
            self.last_player_activity_dict[player_object.name][self.name] = {}

        self.last_player_activity_dict[player_object.name][self.name].update({"player_crossed_outside_boundary_from_inside": player_is_inside_boundary})

        if player_is_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_was_inside_boundary:
                return True
            else:
                return False

    def player_crossed_inside_core_from_boundary(self, player_object):
        player_is_inside_boundary = self.player_is_inside_core(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.name][self.name]["player_crossed_inside_core_from_boundary"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.name not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.name] = {}
        elif self.name not in self.last_player_activity_dict[player_object.name]:
            self.last_player_activity_dict[player_object.name][self.name] = {}

        self.last_player_activity_dict[player_object.name][self.name].update({"player_crossed_inside_core_from_boundary": player_is_inside_boundary})

        if player_was_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_is_inside_boundary:
                return True
            else:
                return False

    def player_crossed_inside_boundary_from_core(self, player_object):
        player_is_inside_boundary = self.player_is_inside_core(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.name][self.name]["player_crossed_inside_boundary_from_core"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.name not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.name] = {}
        elif self.name not in self.last_player_activity_dict[player_object.name]:
            self.last_player_activity_dict[player_object.name][self.name] = {}

        self.last_player_activity_dict[player_object.name][self.name].update({"player_crossed_inside_boundary_from_core": player_is_inside_boundary})

        if player_is_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_was_inside_boundary:
                return True
            else:
                return False
