import math


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

    rot_old = {}
    pos_old = {}

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)
        self.region = self.__get_region_string(self.pos_x, self.pos_z)

    def __get_region_string(self, pos_x, pos_z):
        grid_x = int(math.floor(pos_x / 512))
        grid_z = int(math.floor(pos_z / 512))

        return str(grid_x) + "." + str(grid_z) + ".7.rg"

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def store_player_lifesigns(self):
        self.rot_old.update({"rot_x": self.rot_x, "rot_y": self.rot_y, "rot_z": self.rot_z})
        self.pos_old.update({"pos_x": self.pos_x, "pos_y": self.pos_y, "pos_z": self.pos_z})

    def check_if_lifesigns_have_changed(self):
        if self.rot_x != self.rot_old["rot_x"] or self.rot_y != self.rot_old["rot_y"] or self.rot_z != self.rot_old["rot_z"]:
            return True
        if self.pos_x != self.pos_old["pos_x"] or self.pos_y != self.pos_old["pos_y"] or self.pos_z != self.pos_old["pos_z"]:
            return True
        return False
