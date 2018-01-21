import math


class Location(object):
    owner = str
    name = str
    description = str

    messages_dict = {
        "leaving_core": "leaving core",
        "leaving_boundary": "leaving boundary",
        "entering_boundary": "entering boundary",
        "entering_core": "entering core"
    }

    # the center of the shape
    pos_x = float
    pos_y = float
    pos_z = float

    # sphere and cube so far
    shape = str

    # spheres and cubes
    radius = float
    boundary_radius = float

    # cuboids (rooms)
    width = int
    length = int
    height = int

    boundary_percentage = 33
    # Todo: region should be a list as a location and it's effect can spawn several regions. capture all regions if empty
    region = list

    last_player_activity_dict = {}

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_owner(self, owner):
        self.owner = owner
        return True

    def set_name(self, name):
        self.name = name
        return True

    def set_description(self, description):
        self.description = description
        return True

    def set_coordinates(self, pos_x, pos_y, pos_z):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        return True

    def set_shape(self, shape):
        allowed_shapes = ['cube', 'sphere']
        if shape in allowed_shapes:
            self.shape = shape
            return True
        return False

    def set_radius(self, player_object):
        radius = float(
            math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2)
        )
        allowed_range = range(5, 100 + 1)
        if int(radius * 2) in allowed_range:
            self.radius = radius
            return True
        return False

    def set_boundary_radius(self, player_object):
        radius = float(
            math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2)
        )
        allowed_range = range(5, self.radius + 1)
        if int(radius) in allowed_range:
            self.radius = radius
            return True
        return False

    def set_width(self, width):
        self.width = width
        return True

    def set_length(self, length):
        self.length = length
        return True

    def set_height(self, height):
        self.height = height
        return True

    def set_messages(self, messages_dict):
        self.messages_dict = messages_dict

    def player_is_inside_boundary(self, player_object):
        """ calculate the position of a player against a location

        for now we have only a sphere and cube

        next will be rooms, then polygons for more exotic bases. the goal is to use exactly the
        space one needs instead of arbitrary shapes dictated by my lack of math-skills!

        got some math-skills? contact me :)
        """
        player_is_inside_boundary = 0
        if self.shape == "sphere":
            """ we determine the location by the locations radius and the distance of the player from it's center,
            spheres make this especially easy, so I picked them first ^^
            """
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
            player_is_inside_boundary = distance_to_location_center <= float(self.radius)
        if self.shape == "cube":
            """ we determine the are of the location by the locations center, it's width, height and length ^^
            """
            if float(player_object.pos_x) >= (float(self.pos_x) - float(self.radius)) and float(player_object.pos_x) <= (float(self.pos_x) + float(self.radius)) and float(player_object.pos_y) >= (float(self.pos_y)) and float(player_object.pos_y) <= (float(self.pos_y) + (float(self.radius) * 2)) and float(player_object.pos_z) >= (float(self.pos_z) - float(self.radius)) and float(player_object.pos_z) <= (float(self.pos_z) + float(self.radius)):
                player_is_inside_boundary = True

        return player_is_inside_boundary

    def player_is_inside_core(self, player_object):
        player_is_inside_core = 0
        if self.shape == "sphere":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
            distance_to_core_boundary = (float(self.radius) / 100) * (100 - float(self.boundary_percentage))
            player_is_inside_core = distance_to_location_center <= distance_to_core_boundary
        if self.shape == "cube":
            if float(player_object.pos_x) >= (float(self.pos_x) - ((float(self.radius) / 100) * (100 - float(self.boundary_percentage)))) and float(player_object.pos_x) <= (float(self.pos_x) + ((((float(self.radius) / 100) * (100 - float(self.boundary_percentage))) / 100) * (100 - float(self.boundary_percentage)))) and float(player_object.pos_y) >= (float(self.pos_y)) and float(player_object.pos_y) <= (float(self.pos_y) + (((float(self.radius) * 2) / 100) * (100 - float(self.boundary_percentage)))) and float(player_object.pos_z) >= (float(self.pos_z) - ((float(self.radius) / 100) * (100 - float(self.boundary_percentage)))) and float(player_object.pos_z) <= (float(self.pos_z) + ((float(self.radius) / 100) * (100 - float(self.boundary_percentage)))):
                player_is_inside_core = True

        return player_is_inside_core

    def player_crossed_outside_boundary_from_outside(self, player_object):
        """ determine if the given player is inside a locations perimeter, and check if the previously stored
        player-position, if any, was outside of the locations perimeter.

        update the last known state for use in the next call

        this is used to trigger events on entering a locations perimeter for example
        """
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        try:
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.name][self.owner]["player_crossed_outside_boundary_from_outside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        if self.name not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.name] = {}
        if self.owner not in self.last_player_activity_dict[player_object.steamid][self.name]:
            self.last_player_activity_dict[player_object.steamid][self.name][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.name][self.owner].update({"player_crossed_outside_boundary_from_outside": player_is_inside_boundary})

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
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.name][self.owner]["player_crossed_outside_boundary_from_inside"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        if self.name not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.name] = {}
        if self.owner not in self.last_player_activity_dict[player_object.steamid][self.name]:
            self.last_player_activity_dict[player_object.steamid][self.name][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.name][self.owner].update({"player_crossed_outside_boundary_from_inside": player_is_inside_boundary})

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
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.name][self.owner]["player_crossed_inside_core_from_boundary"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        if self.name not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.name] = {}
        if self.owner not in self.last_player_activity_dict[player_object.steamid][self.name]:
            self.last_player_activity_dict[player_object.steamid][self.name][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.name][self.owner].update({"player_crossed_inside_core_from_boundary": player_is_inside_boundary})

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
            player_was_inside_boundary = self.last_player_activity_dict[player_object.steamid][self.name][self.owner]["player_crossed_inside_boundary_from_core"]
        except (TypeError, KeyError):
            player_was_inside_boundary = player_is_inside_boundary

        if player_object.steamid not in self.last_player_activity_dict:
            self.last_player_activity_dict[player_object.steamid] = {}
        if self.name not in self.last_player_activity_dict[player_object.steamid]:
            self.last_player_activity_dict[player_object.steamid][self.name] = {}
        if self.owner not in self.last_player_activity_dict[player_object.steamid][self.name]:
            self.last_player_activity_dict[player_object.steamid][self.name][self.owner] = {}

        self.last_player_activity_dict[player_object.steamid][self.name][self.owner].update({"player_crossed_inside_boundary_from_core": player_is_inside_boundary})

        if player_is_inside_boundary:  # no need to do anything if player was already in
            return False
        else:
            if player_was_inside_boundary:
                return True
            else:
                return False

