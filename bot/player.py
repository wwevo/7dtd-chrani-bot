import math
from bot.logger import logger


class Player():
    id = long
    name = str
    permission_levels = list
    pos_x = float
    pos_y = float
    pos_z = float
    rot_x = float
    rot_y = float
    rot_z = float
    death_x = float
    death_y = float
    death_z = float
    remote = bool
    health = int
    deaths = int
    zombies = int
    players = int
    score = int
    level = int
    steamid = str
    ip = str
    ping = int
    region = str
    country_code = str
    authenticated = bool
    web_auth = bool
    is_responsive = bool
    last_teleport = int

    def get_id(self):
        return unicode(self.steamid)

    def __init__(self, **kwargs):
        self.last_teleport = 0
        self.is_responsive = False
        self.permission_levels = []
        self.web_auth = False
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

        try:
            self.region = self.__get_region_string(self.pos_x, self.pos_z)
        except Exception:
            pass

    def __get_region_string(self, pos_x, pos_z):
        grid_x = int(math.floor(pos_x / 512))
        grid_z = int(math.floor(pos_z / 512))

        return str(grid_x) + "." + str(grid_z) + ".7rg"

    def set_name(self, name):
        self.name = name

    def set_country_code(self, country_code):
        self.country_code = country_code

    def get_country_code(self):
        if isinstance(self.country_code, basestring):
            return str(self.country_code)
        else:
            return None

    def switch_on(self, source=""):
        self.is_responsive = True
        logger.info("switched on player '{}' - {}".format(self.name, source))

    def switch_off(self, source=""):
        self.is_responsive = False
        logger.info("switched off player '{}' - {}".format(self.name, source))

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_authenticated(self, authenticated):
        self.authenticated = authenticated
        return True

    def set_permission_levels(self, level_list):
        self.permission_levels = level_list

    def add_permission_level(self, level):
        if level not in self.permission_levels:
            self.permission_levels.append(level)

    def has_permission_level(self, level):
        if level in self.permission_levels:
            return True

    def remove_permission_level(self, level):
        if level in self.permission_levels:
            self.permission_levels.remove(level)

    def set_coordinates(self, location_object):
        self.pos_x = location_object.tele_x
        self.pos_y = location_object.tele_y
        self.pos_z = location_object.tele_z
        return True

    def has_health(self):
        if int(self.health) is not 0:
            return True
        else:
            return False

    def is_dead(self):
        if int(self.health) == 0:
            return True
        else:
            return False
