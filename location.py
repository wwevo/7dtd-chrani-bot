import math


class Location(object):
    owner = str
    name = str
    description = str
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
        """ calculate the position of a player against a location

        for now we have only a sphere

        next will be cubes and rooms, then polygons for more exotic bases. the goal is to use exactly the
        space one needs instead of arbitrary shapes dictated by my lack of math-skills!

        got some math-skills? contact me :)
        """
        is_inside_boundary = 0
        if self.shape == "sphere":
            """ we determine the location by the locations radius and the distance of the player from it's center,
            spheres make this especially easy, so I picked them first ^^
            """
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
            is_inside_boundary = distance_to_location_center <= float(self.radius)

        if self.shape == "room":
            """ we determine the location by the locations radius and the distance of the player from it's center,
            spheres make this especially easy, so I picked them first ^^
            """
            distance_to_location_center = 0
            is_inside_boundary = distance_to_location_center <= float(self.radius)

        player_is_inside_boundary = is_inside_boundary
        # print "player_is_inside_boundary: {} of {}".format(player_is_inside_boundary, self.name)
        return player_is_inside_boundary

    def player_is_inside_core(self, player_object):
        distance_to_location_center = 0
        if self.shape == "sphere":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
        # pretty much the same as player_is_inside_boundary(), but we subtract the boundary_percentage from the radius
        distance_to_core_boundary = (float(self.radius) / 100) * (100 - float(self.boundary_percentage))
        player_is_inside_core = distance_to_location_center <= distance_to_core_boundary

        # print "player_is_inside_core: {} of {}".format(player_is_inside_core, self.name)
        return player_is_inside_core

    def player_crossed_outside_boundary_from_outside(self, player_object):
        """ determine if the given player is inside a locations perimeter, and check if the previously stored
        player-position, if any, was outside of the locations perimeter.

        update the last known state for use in the next call

        this is used to trigger events on entering a locations perimeter for example
        """
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.owner]["player_crossed_outside_boundary_from_outside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        if self.owner not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.owner].update({"player_crossed_outside_boundary_from_outside": player_is_inside_boundary})

        if player_was_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_is_inside_boundary:
                return True
            else:
                return False

    def player_crossed_outside_boundary_from_inside(self, player_object):
        """ determine if the given player is outside a locations perimeter, and check if the previously stored
        player-position, if any, was inside of the locations perimeter.

        update the last known state for use in the next call

        this is used to trigger events on exiting a locations perimeter for example
        """
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.owner]["player_crossed_outside_boundary_from_inside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        elif self.owner not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.owner].update({"player_crossed_outside_boundary_from_inside": player_is_inside_boundary})

        if player_is_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_was_inside_boundary:
                return True
            else:
                return False

    def player_crossed_inside_core_from_boundary(self, player_object):
        """ determine if the given player is inside a locations core, and check if the previously stored
        player-position, if any, was outside of the locations core.

        update the last known state for use in the next call

        this is used to trigger events on entering a locations core-area for example
        """
        player_is_inside_boundary = self.player_is_inside_core(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.owner]["player_crossed_inside_core_from_boundary"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        elif self.owner not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.owner].update({"player_crossed_inside_core_from_boundary": player_is_inside_boundary})

        if player_was_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_is_inside_boundary:
                return True
            else:
                return False

    def player_crossed_inside_boundary_from_core(self, player_object):
        """ determine if the given player is outside a locations core, and check if the previously stored
        player-position, if any, was inside of the locations core.

        update the last known state for use in the next call

        this is used to trigger events on leaving a locations core-area for example
        """
        player_is_inside_boundary = self.player_is_inside_core(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.owner]["player_crossed_inside_boundary_from_core"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        elif self.owner not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.owner].update({"player_crossed_inside_boundary_from_core": player_is_inside_boundary})

        if player_is_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_was_inside_boundary:
                return True
            else:
                return False
