import math
from logger import logger


class Player(object):
    id = long
    name = str
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
    is_responsive = bool
    last_teleport = int

    def __init__(self, **kwargs):
        self.last_teleport = 0
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

        try:
            self.region = self.__get_region_string(self.pos_x, self.pos_z)
        except:
            pass

    def __get_region_string(self, pos_x, pos_z):
        grid_x = int(math.floor(pos_x / 512))
        grid_z = int(math.floor(pos_z / 512))

        return str(grid_x) + "." + str(grid_z) + ".7rg"

    def set_name(self, name):
        self.name = name

    def set_country_code(self, country_code):
        self.country_code = country_code

    def switch_on(self, source=""):
        self.is_responsive = True
        # self.store_player_lifesigns()
        logger.info("switched on player " + self.name + " " + source)

    def switch_off(self, source=""):
        self.is_responsive = False
        # self.store_player_lifesigns()
        logger.info("switched off player " + self.name + " " + source)

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_authenticated(self, authenticated):
        self.authenticated = authenticated
        return True

    def set_coordinates(self,location_object):
        self.pos_x = location_object.tele_x
        self.pos_y = location_object.tele_y
        self.pos_z = location_object.tele_z
        return True

    def is_alive(self):
        if self.health is not 0:
            return True
        else:
            return False

    def is_dead(self):
        if self.health == 0:
            return True
        else:
            return False
