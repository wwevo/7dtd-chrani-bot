import math


class Location(object):
    identifier = str
    owner = str
    name = str
    description = str

    messages_dict = dict

    # the center of the shape
    pos_x = float
    pos_y = float
    pos_z = float

    tele_x = float
    tele_y = float
    tele_z = float

    # sphere and cube so far
    shape = str

    # spheres and cubes
    radius = float
    warning_boundary = float

    # cuboids (rooms)
    width = int
    length = int
    height = int

    boundary_percentage = int

    # TODO: region should be a list as a location and it's effect can spawn several regions. capture all regions if empty
    region = list

    last_player_activity_dict = {}
    list_of_players_inside = []

    def __init__(self, **kwargs):
        self.messages_dict = {
            "leaving_core": "leaving core",
            "leaving_boundary": "leaving boundary",
            "entering_boundary": "entering boundary",
            "entering_core": "entering core"
        }
        self.radius = 10
        self.width = self.radius * 2
        self.length = self.radius * 2
        self.height = self.radius * 2
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_owner(self, owner):
        self.owner = owner
        return True

    def set_name(self, name):
        self.name = name
        return True

    def set_identifier(self, name):
        keepcharacters = '_'
        identifier = "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
        self.identifier = identifier
        return identifier

    def set_description(self, description):
        self.description = description
        return True

    def set_coordinates(self, player_object):
        self.pos_x = player_object.pos_x
        self.pos_y = player_object.pos_y
        self.pos_z = player_object.pos_z
        self.set_teleport_coordinates(player_object)
        return True

    def set_center(self, player_object, width, length, height):
        self.pos_x = player_object.pos_x + (float(width) / 2)
        self.pos_y = player_object.pos_y
        self.pos_z = player_object.pos_z + (float(length) / 2)
        return True

    def set_teleport_coordinates(self, player_object):
        if self.name == 'spawn' or self.player_is_inside_boundary(player_object):
            self.tele_x = player_object.pos_x
            self.tele_y = player_object.pos_y
            self.tele_z = player_object.pos_z
            return True
        else:
            return False

    def set_shape(self, shape):
        allowed_shapes = ['cube', 'sphere', 'room']
        if shape in allowed_shapes:
            self.shape = shape
            if shape == 'sphere':
                self.radius = max(
                    self.width / 2,
                    self.length / 2
                )
            return True
        return False

    def set_radius(self, player_object):
        radius = float(
            math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2)
        )
        allowed_range = range(3, 141)
        if int(radius) in allowed_range:
            self.radius = radius
            self.width = self.radius * 2
            self.length = self.radius * 2
            self.height = self.radius * 2
            return True, allowed_range
        return radius, allowed_range

    def set_warning_boundary(self, player_object):
        radius = float(
            math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2)
        )
        allowed_range = range(3, int(self.radius + 1))
        if int(radius) in allowed_range:
            self.warning_boundary = radius
            return True, allowed_range
        return radius, allowed_range

    def set_width(self, width):
        allowed_range = range(3, 141)
        self.width = width
        return True, allowed_range

    def set_length(self, length):
        allowed_range = range(3, 141)
        self.length = length
        return True, allowed_range

    def set_height(self, height):
        allowed_range = range(3, 141)
        self.height = height
        return True, allowed_range

    def set_messages(self, messages_dict):
        self.messages_dict = messages_dict

    def get_messages_dict(self):
        return self.messages_dict

    def set_region(self, regions_list):
        self.region = regions_list

    def set_list_of_players_inside(self, list_of_players_inside):
        self.list_of_players_inside = list_of_players_inside

    def player_is_inside_boundary(self, player_object):
        """ calculate the position of a player against a location

        for now we have only a sphere and cube

        next will be rooms, then polygons for more exotic bases. the goal is to use exactly the
        space one needs instead of arbitrary shapes dictated by my lack of math-skills!

        got some math-skills? contact me :)
        """
        player_is_inside_boundary = False
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
            """ we determine the area of the location by the locations center and it's radius (half a sides-length)
            """
            if (float(self.pos_x) - float(self.radius)) <= float(player_object.pos_x) <= (float(self.pos_x) + float(self.radius)) and (float(self.pos_y) - float(self.radius)) <= float(player_object.pos_y) <= (float(self.pos_y) + float(self.radius)) and (float(self.pos_z) - float(self.radius)) <= float(player_object.pos_z) <= (float(self.pos_z) + float(self.radius)):
                player_is_inside_boundary = True
        if self.shape == "room":
            """ we determine the area of the location by the locations center, it's width, height and length. height will be calculated from ground level (-1) upwards 
            """
            if (float(self.pos_x) - float(self.width) / 2) <= float(player_object.pos_x) <= (float(self.pos_x) + float(self.width) /2) and float(self.pos_y) <= float(player_object.pos_y) + 1 <= (float(self.pos_y) + float(self.height)) and (float(self.pos_z) - float(self.length) / 2) <= float(player_object.pos_z) <= (float(self.pos_z) + float(self.length) / 2):
                player_is_inside_boundary = True

        return player_is_inside_boundary

    def get_player_status(self, player_object):
        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        if player_is_inside_boundary == True:
            # player is inside
            if player_object.steamid in self.list_of_players_inside:
                # and already was inside the location
                return 'is inside'
            else:
                # newly entered the location
                self.list_of_players_inside.append(player_object.steamid)
                return 'has entered'
        else:
            # player is outside
            if player_object.steamid in self.list_of_players_inside:
                # and was inside before, so he left the location
                self.list_of_players_inside.remove(player_object.steamid)
                return 'has left'
            else:
                # and already was outside before
                return None
