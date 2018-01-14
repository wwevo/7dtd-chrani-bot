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

    authenticated = False
    is_responsive = False

    lifesigns_dict_old = {}

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)
        self.region = self.__get_region_string(self.pos_x, self.pos_z)

    def __get_region_string(self, pos_x, pos_z):
        grid_x = int(math.floor(pos_x / 512))
        grid_z = int(math.floor(pos_z / 512))

        return str(grid_x) + "." + str(grid_z) + ".7rg"

    def switch_on(self, source=""):
        self.is_responsive = True
        # self.store_player_lifesigns()
        logger.debug("switched on player " + self.name + " " + source)

    def switch_off(self, source=""):
        self.is_responsive = False
        # self.store_player_lifesigns()
        logger.debug("switched off player " + self.name + " " + source)

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def store_player_lifesigns(self):
        self.lifesigns_dict_old.update({
            "rot_x": self.rot_x, "rot_y": self.rot_y, "rot_z": self.rot_z, "pos_x": self.pos_x, "pos_y": self.pos_y, "pos_z": self.pos_z}
        )

    def check_if_lifesigns_have_changed(self):
        """ compares playerdata that is bound to change often

        i was having troubles with rounding, in fact, i still do. converting this to integers does help a litle,
        but i believe in boundary cases it can still misfire
        """
        if self.rot_x != self.lifesigns_dict_old["rot_x"]\
                or int(self.rot_y) != int(self.lifesigns_dict_old["rot_y"])\
                or int(self.rot_z) != int(self.lifesigns_dict_old["rot_z"])\
                or int(self.pos_x) != int(self.lifesigns_dict_old["pos_x"])\
                or int(self.pos_y) != int(self.lifesigns_dict_old["pos_y"])\
                or int(self.pos_z) != int(self.lifesigns_dict_old["pos_z"]):
            return True
        return False

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

    def get_lifesigns_dict(self):
        lifesigns_dict = {
            "rot_x": self.rot_x, "rot_y": self.rot_y, "rot_z": self.rot_z, "pos_x": self.pos_x, "pos_y": self.pos_y, "pos_z": self.pos_z
        }
        return lifesigns_dict

    def get_lifesigns_old_dict(self):
        return self.lifesigns_dict_old
