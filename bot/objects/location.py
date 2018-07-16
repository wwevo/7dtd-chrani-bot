import math
import random
from bot.assorted_functions import get_region_string


# noinspection SpellCheckingInspection
class Location(object):
    enabled = bool
    is_public = bool

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

    protected_core = bool
    protected_core_whitelist = list

    # cuboids (rooms)
    width = int
    length = int
    height = int

    region_list = list

    last_player_activity_dict = {}

    list_of_players_inside = list
    list_of_players_inside_core = list

    def __init__(self, **kwargs):
        self.messages_dict = {
            "entered_location": "entering boundary",
            "entered_locations_core": "entering core",
            "left_locations_core": "leaving core",
            "left_location": "leaving boundary"
        }
        self.radius = 20
        self.is_public = False
        self.warning_boundary = 16
        self.width = self.radius * 2
        self.length = self.radius * 2
        self.height = self.radius * 2
        self.region_list = []
        self.enabled = True
        self.list_of_players_inside = []
        self.list_of_players_inside_core = []
        self.protected_core = False
        self.protected_core_whitelist = []

        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)
        self.update_region_list()

    def set_owner(self, owner):
        self.owner = owner
        return True

    def set_name(self, name):
        self.name = name
        return True

    def set_identifier(self, identifier):
        sanitized_identifier = "".join(i for i in identifier if i not in r' \/:*?"<>|!.,;')
        self.identifier = sanitized_identifier
        return sanitized_identifier

    def set_description(self, description):
        self.description = description
        return True

    def set_coordinates(self, player_object):
        self.pos_x = player_object.pos_x
        self.pos_y = player_object.pos_y
        self.pos_z = player_object.pos_z
        self.set_teleport_coordinates(player_object)
        self.update_region_list()
        return True

    # noinspection PyUnusedLocal
    def set_center(self, player_object, width, length, height):
        self.pos_x = player_object.pos_x + (float(width) / 2)
        self.pos_y = player_object.pos_y
        self.pos_z = player_object.pos_z + (float(length) / 2)
        self.update_region_list()
        return True

    def set_teleport_coordinates(self, player_object):
        if self.player_is_inside_boundary(player_object):
            self.tele_x = player_object.pos_x
            self.tele_y = player_object.pos_y
            self.tele_z = player_object.pos_z
            return True
        else:
            return False

    def set_shape(self, shape):
        allowed_shapes = ['cube', 'sphere', 'room']
        if shape not in allowed_shapes or shape == self.shape:
            return False

        self.shape = shape
        if shape in ['sphere', 'cube']:
            self.radius = max(
                self.width / 2,
                self.length / 2
            )
        self.update_region_list()
        return True

    def get_distance(self, coords):
        distance = float(
            math.sqrt(
                (float(self.pos_x) - float(coords[0])) ** 2 + (
                        float(self.pos_y) - float(coords[1])) ** 2 + (
                        float(self.pos_z) - float(coords[2])) ** 2)
        )
        return int(distance)

    def set_radius(self, radius):
        allowed_range = range(3, 2048)
        if int(radius) in allowed_range:
            self.radius = radius
            self.width = self.radius * 2
            self.length = self.radius * 2
            self.height = self.radius * 2
            self.update_region_list()
            return True, radius

        return radius, allowed_range

    def set_warning_boundary(self, radius):
        allowed_range = range(0, int(self.radius))
        if int(radius) in allowed_range:
            self.warning_boundary = radius
            return True, radius
        return radius, allowed_range

    def set_width(self, width):
        allowed_range = range(3, 2048)
        self.width = width
        self.update_region_list()
        return True, allowed_range

    def set_length(self, length):
        allowed_range = range(3, 2048)
        self.length = length
        self.update_region_list()
        return True, allowed_range

    def set_height(self, height):
        allowed_range = range(3, 2048)
        self.height = height
        # no region update here, since regions are only projected on a two dimensional grid
        # self.update_region_list()
        return True, allowed_range

    def set_messages(self, messages_dict):
        self.messages_dict = messages_dict

    def get_messages_dict(self):
        return self.messages_dict

    def set_protected_core(self, protected):
        self.protected_core = protected
        return True

    def set_visibility(self, is_public):
        if is_public is True:
            self.is_public = True
        else:
            self.is_public = False

        return True

    # TODO: region should be a list as a location and it's effect can spawn several regions. capture all regions if empty
    def update_region_list(self):
        # a'ight, I suck at maths. Still need this to be done so here it goes.
        self.region_list = []
        if self.shape == "sphere":
            # let's convert everything to rectangles first, the fancy stuff can come later
            # determine the top left corner of the square the circle occupies
            top = self.pos_z - self.radius
            left = self.pos_x - self.radius
            # radius * 2 divided by the region size rounded up, to get the total regions span. Add one to get the total possible width and height
            width_in_regions = math.ceil(float(2 * self.radius) / 512) + 1
            height_in_regions = math.ceil(float(2 * self.radius) / 512) + 1
        elif self.shape == "cube" or self.shape == "room":
            # untested
            top = self.pos_z
            left = self.pos_x
            width_in_regions = math.ceil(float(self.width) / 512) + 1
            height_in_regions = math.ceil(float(self.height) / 512) + 1
        else:
            return False

        # translate occupied coordinates into the region-grid provided by allocs webmap
        for column in range(int(width_in_regions + 1)):
            for row in range(int(height_in_regions + 1)):
                self.region_list.append(get_region_string(left + ((column - 1) * 512), top - ((row - 1) * 512)))

        return self.region_list

    def set_list_of_players_inside(self, list_of_players_inside):
        self.list_of_players_inside = list_of_players_inside

    def set_list_of_players_inside_core(self, list_of_players_inside_core):
        self.list_of_players_inside_core = list_of_players_inside_core

    def get_ejection_coords_tuple(self, player_object):
        if self.shape == "sphere":
            angle = random.randint(0, 359)
            x = self.pos_x + (self.radius + 2) * math.cos(angle)
            z = self.pos_z + (self.radius + 2) * math.sin(angle)
            coords = (x, -1, z)
        elif self.shape == "cube" or self.shape == "room":
            # untested
            return False
        else:
            return False

        return coords

    def player_is_inside_boundary(self, player_object):
        """ calculate the position of a player against a location

        for now we have only a spheres and cubics

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
            if (float(self.pos_x) - float(self.width) / 2) <= float(player_object.pos_x) <= (float(self.pos_x) + float(self.width) / 2) and float(self.pos_y) <= float(player_object.pos_y) + 1 <= (float(self.pos_y) + float(self.height)) and (float(self.pos_z) - float(self.length) / 2) <= float(player_object.pos_z) <= (float(self.pos_z) + float(self.length) / 2):
                player_is_inside_boundary = True

        return player_is_inside_boundary

    def player_is_inside_core(self, player_object):
        player_is_inside_core = False
        if self.shape == "sphere":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))
            player_is_inside_core = distance_to_location_center <= float(self.warning_boundary)
        if self.shape == "cube":
            if (float(self.pos_x) - float(self.warning_boundary)) <= float(player_object.pos_x) <= (float(self.pos_x) + float(self.warning_boundary)) and (float(self.pos_y) - float(self.warning_boundary)) <= float(player_object.pos_y) <= (float(self.pos_y) + float(self.warning_boundary)) and (float(self.pos_z) - float(self.warning_boundary)) <= float(player_object.pos_z) <= (float(self.pos_z) + float(self.warning_boundary)):
                player_is_inside_core = True
        if self.shape == "room":
            # TODO: this has to be adjusted. it's just copied from the boundary function
            if (float(self.pos_x) - float(self.width) / 2) <= float(player_object.pos_x) <= (float(self.pos_x) + float(self.width) / 2) and float(self.pos_y) <= float(player_object.pos_y) + 1 <= (float(self.pos_y) + float(self.height)) and (float(self.pos_z) - float(self.length) / 2) <= float(player_object.pos_z) <= (float(self.pos_z) + float(self.length) / 2):
                player_is_inside_core = True

        return player_is_inside_core

    def get_player_status(self, player_object):
        player_status = None

        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        if player_is_inside_boundary is True:
            # player is inside
            if player_object.steamid in self.list_of_players_inside:
                # and already was inside the location
                player_status = 'is inside'
            else:
                # newly entered the location
                self.list_of_players_inside.append(player_object.steamid)
                player_status = 'has entered'
        else:
            # player is outside
            if player_object.steamid in self.list_of_players_inside:
                # and was inside before, so he left the location
                self.list_of_players_inside.remove(player_object.steamid)
                player_status = 'has left'
            else:
                # and already was outside before
                player_status = 'is outside'

        player_is_inside_core = self.player_is_inside_core(player_object)
        if player_is_inside_core is True:
            # player is inside core
            if player_object.steamid in self.list_of_players_inside_core:
                # and already was inside the location
                player_status = 'is inside core'
            else:
                # newly entered the location
                self.list_of_players_inside_core.append(player_object.steamid)
                player_status = 'has entered core'
        else:
            # player is outside
            if player_object.steamid in self.list_of_players_inside_core:
                # and was inside before, so he left the core
                self.list_of_players_inside_core.remove(player_object.steamid)
                player_status = 'has left core'

        return player_status
