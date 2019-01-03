import __main__
import math
import random
from bot.assorted_functions import get_region_string
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger


# noinspection SpellCheckingInspection
class Location(object):
    enabled = bool
    is_public = bool

    identifier = str
    owner = str
    name = str
    description = str

    messages_dict = dict
    show_messages = bool
    show_warning_messages = bool

    # the center of the shape
    pos_x = float
    pos_y = float
    pos_z = float

    tele_x = float
    tele_y = float
    tele_z = float

    type = str
    # sphere, cube, circle and square so far
    shape = str

    # spheres and cubes
    radius = float
    warning_boundary = float

    teleport_target = str
    teleport_active = bool

    protected_core = bool
    protected_core_whitelist = list

    # cuboids (rooms)
    width = int
    length = int
    height = int

    region_list = list

    list_of_players_inside = list
    list_of_players_inside_core = list

    def __init__(self, **kwargs):
        self.messages_dict = {
            "entered_location": "entering boundary",
            "entered_locations_core": "entering core",
            "left_locations_core": "leaving core",
            "left_location": "leaving boundary"
        }
        self.show_messages = True
        self.show_warning_messages = False
        self.radius = 20
        self.description = None
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
        self.teleport_target = None
        self.teleport_active = False
        self.type = "standard location"

        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_owner(self, owner):
        self.owner = owner
        return True

    def set_name(self, name):
        self.name = name
        return True

    def create_identifier(self, name):
        sanitized_name = "".join(i for i in name if i not in r' \/:*?"<>|!.,;')
        return sanitized_name

    def set_identifier(self, identifier):
        self.identifier = identifier
        return True

    def set_description(self, description):
        self.description = description
        return True

    def set_coordinates(self, player_object):
        self.pos_x = player_object.pos_x
        self.pos_y = player_object.pos_y
        self.pos_z = player_object.pos_z
        self.tele_x = player_object.pos_x
        self.tele_y = player_object.pos_y
        self.tele_z = player_object.pos_z
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

    def get_teleport_coordinates(self):
        if self.tele_x != self.pos_x or self.tele_y != self.pos_y or self.tele_z != self.pos_z:
            return self.tele_x, self.tele_y, self.tele_z
        else:
            return self.pos_x, self.pos_y, self.pos_z

    def set_shape(self, shape):
        allowed_shapes = ['sphere', 'cube', 'circle', 'square']
        if shape not in allowed_shapes or shape == self.shape:
            return False

        self.shape = shape
        if shape in ['sphere', 'cube', 'circle', 'square']:
            self.radius = max(
                float(self.width) / 2,
                float(self.length) / 2
            )
        self.update_region_list()
        return True

    def set_type(self, type):
        allowed_types = ['standard', 'village', 'teleport']
        if type not in allowed_types or type == self.type:
            return False

        self.type = type
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
        return True, allowed_range

    def set_messages(self, messages_dict):
        self.messages_dict = messages_dict

    def get_messages_dict(self):
        return self.messages_dict

    def set_protected_core(self, protected):
        self.protected_core = protected
        self.show_warning_messages = protected

        return True

    def set_visibility(self, is_public):
        if is_public is True:
            self.is_public = True
        else:
            self.is_public = False

        return True

    def update_region_list(self):
        # a'ight, I suck at maths. Still need this to be done so here it goes.
        self.region_list = []
        if self.shape in ["sphere", "circle"]:
            # let's convert everything to rectangles first, the fancy stuff can come later
            # determine the top left corner of the square the circle occupies
            top = self.pos_z - self.radius
            left = self.pos_x - self.radius
            # radius * 2 divided by the region size rounded up, to get the total regions span. Add one to get the total possible width and length
            width_in_regions = math.ceil(float(self.radius) / 512) * 2
            length_in_regions = math.ceil(float(self.radius) / 512) * 2
        elif self.shape in ["cube", "square"]:
            # untested
            top = self.pos_z
            left = self.pos_x
            width_in_regions = math.ceil(float(self.width / 2) / 512) * 2
            length_in_regions = math.ceil(float(self.height / 2) / 512) * 2
        else:
            return False

        # translate occupied coordinates into the region-grid provided by allocs webmap
        for column in range(int(width_in_regions + 1)):
            for row in range(int(length_in_regions + 1)):
                if row == 0 or column == 0:
                    continue
                self.region_list.append(get_region_string(left + ((column - 1) * 512), top + ((row - 1) * 512)))

        return self.region_list

    def set_list_of_players_inside(self, list_of_players_inside):
        self.list_of_players_inside = list_of_players_inside

    def set_list_of_players_inside_core(self, list_of_players_inside_core):
        self.list_of_players_inside_core = list_of_players_inside_core

    def get_ejection_coords_tuple(self):
        if self.shape in ["circle", "sphere"]:
            angle = random.randint(0, 359)
            x = self.pos_x + (self.radius + 2) * math.cos(angle)
            z = self.pos_z + (self.radius + 2) * math.sin(angle)
            coords = (x, -1, z)
        elif self.shape in ["square", "cube"]:  # yeah, using the circle shit here ^^
            angle = random.randint(0, 359)
            x = self.pos_x + (self.radius + 2) * math.cos(angle)
            z = self.pos_z + (self.radius + 2) * math.sin(angle)
            coords = (x, -1, z)
        else:
            return False

        return coords

    def get_teleport_coords_tuple(self):
        return self.tele_x, self.tele_y, self.tele_z

    def position_is_inside_boundary(self, position_tuple):
        position_is_inside_boundary = False
        if self.shape == "sphere":
            """ we determine the location by the locations radius and the distance of the player from it's center,
            spheres make this especially easy, so I picked them first ^^
            """
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(position_tuple[0])) ** 2 + (
                    float(self.pos_y) - float(position_tuple[1])) ** 2 + (
                    float(self.pos_z) - float(position_tuple[2])) ** 2))
            position_is_inside_boundary = distance_to_location_center <= float(self.radius)
        if self.shape == "cube":
            """ we determine the area of the location by the locations center and it's radius (half a sides-length)
            """
            if (float(self.pos_x) - float(self.radius)) <= float(position_tuple[0]) <= (float(self.pos_x) + float(self.radius)) and (float(self.pos_y) - float(self.radius)) <= float(position_tuple[1]) <= (float(self.pos_y) + float(self.radius)) and (float(self.pos_z) - float(self.radius)) <= float(position_tuple[2]) <= (float(self.pos_z) + float(self.radius)):
                position_is_inside_boundary = True
        if self.shape == "circle":
            """ we determine the location by the locations radius and the distance of the player from it's center ^^
            """
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(position_tuple[0])) ** 2 +
                (float(self.pos_z) - float(position_tuple[2])) ** 2
            ))
            position_is_inside_boundary = distance_to_location_center <= float(self.radius)
        if self.shape == "square":
            if (float(self.pos_x) - float(self.radius)) <= float(position_tuple[0]) <= (float(self.pos_x) + float(self.radius)) and (float(self.pos_z) - float(self.radius)) <= float(position_tuple[2]) <= (float(self.pos_z) + float(self.radius)):
                position_is_inside_boundary = True

        return position_is_inside_boundary

    def player_is_inside_boundary(self, player_object):
        """ calculate the position of a player against a location

        for now we have only a spheres and cubics

        got some math-skills? contact me :)
        """
        chrani_bot = __main__.chrani_bot
        if not player_object.is_online and\
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"] <= 0.0 and \
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"] <= 0.0 and \
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"] <= 0.0:
            logger.debug("Can't check core: No locationdata found for Player {} ".format(player_object.name))
            return None

        try:
            is_it_inside = self.position_is_inside_boundary((
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"],
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"],
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"],
            ))
        except TypeError:
            is_it_inside = None

        return is_it_inside

    def player_is_inside_core(self, player_object):
        chrani_bot = __main__.chrani_bot
        if not player_object.is_online and \
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"] <= 0.0 and \
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"] <= 0.0 and \
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"] <= 0.0:
            logger.debug("Can't check core: No locationdata found for Player {} ".format(player_object.name))
            return None

        player_is_inside_core = False
        if self.shape == "sphere":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"])) ** 2 + (
                    float(self.pos_y) - float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"])) ** 2 + (
                    float(self.pos_z) - float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"])) ** 2))
            player_is_inside_core = distance_to_location_center <= float(self.warning_boundary)
        if self.shape == "cube":
            if (float(self.pos_x) - float(self.warning_boundary)) <= float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"]) <= (float(self.pos_x) + float(self.warning_boundary)) and (float(self.pos_y) - float(self.warning_boundary)) <= float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"]) <= (float(self.pos_y) + float(self.warning_boundary)) and (float(self.pos_z) - float(self.warning_boundary)) <= float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"]) <= (float(self.pos_z) + float(self.warning_boundary)):
                player_is_inside_core = True
        if self.shape == "circle":
            distance_to_location_center = float(math.sqrt(
                (float(self.pos_x) - float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"])) ** 2 + (
                    float(self.pos_z) - float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"])) ** 2))
            player_is_inside_core = distance_to_location_center <= float(self.warning_boundary)
        if self.shape == "square":
            if (float(self.pos_x) - float(self.warning_boundary)) <= float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"]) <= (float(self.pos_x) + float(self.warning_boundary)) and \
                    (float(self.pos_z) - float(self.warning_boundary)) <= float(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"]) <= (float(self.pos_z) + float(self.warning_boundary)):
                player_is_inside_core = True

        return player_is_inside_core

    def get_player_status(self, player_object):
        response_message = ResponseMessage()

        player_is_inside_boundary = self.player_is_inside_boundary(player_object)
        if player_is_inside_boundary is True:
            # player is inside
            if player_object.steamid in self.list_of_players_inside:
                # and already was inside the location
                player_status = 'is inside'
                response_message.add_message(player_status)
            else:
                # newly entered the location
                self.list_of_players_inside.append(player_object.steamid)
                player_status = 'has entered'
                response_message.add_message(player_status)
        else:
            # player is outside
            if player_object.steamid in self.list_of_players_inside:
                # and was inside before, so he left the location
                self.list_of_players_inside.remove(player_object.steamid)
                player_status = 'has left'
                response_message.add_message(player_status)
            else:
                # and already was outside before
                player_status = 'is outside'
                response_message.add_message(player_status)

        player_is_inside_core = self.player_is_inside_core(player_object)
        if player_is_inside_core is True:
            # player is inside core
            if player_object.steamid in self.list_of_players_inside_core:
                # and already was inside the locations core
                player_status = 'is inside core'
                response_message.add_message(player_status)
            else:
                # newly entered the locations core
                self.list_of_players_inside_core.append(player_object.steamid)
                player_status = 'has entered core'
                response_message.add_message(player_status)
        else:
            # player is outside
            if player_object.steamid in self.list_of_players_inside_core:
                # and was inside before, so he left the core
                self.list_of_players_inside_core.remove(player_object.steamid)
                player_status = 'has left core'
                response_message.add_message(player_status)

        return response_message.get_message_dict()

    def get_leaflet_marker_json(self):
        bot = __main__.chrani_bot
        location_list = []
        try:
            location_list = {
                "id": "{}_{}".format(self.owner, self.identifier),
                "owner": self.owner,
                "identifier": self.identifier,
                "name": self.name,
                "owner_name": bot.players.get_by_steamid(self.owner).name,
                "radius": self.radius,
                "inner_radius": self.warning_boundary,
                "protected": self.protected_core,
                "pos_x": self.pos_x,
                "pos_y": self.pos_y,
                "pos_z": self.pos_z,
                "shape": self.shape,
                "type": self.type,
                "layerGroup": self.owner if self.owner == "system" else "locations" if (self.identifier not in bot.settings.get_setting_by_name(name="restricted_names")) else self.identifier
            }
        except KeyError:
            pass

        return location_list

