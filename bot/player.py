from time import time


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
    entityid = str
    ip = str
    ping = int
    region = str
    country_code = str
    authenticated = bool
    is_muted = bool
    last_teleport = int
    last_responsive = float

    def get_id(self):
        return unicode(self.steamid)

    def __init__(self, **kwargs):
        self.last_teleport = 0
        self.is_muted = False
        self.permission_levels = []
        self.last_responsive = time()
        self.entityid = None

        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_name(self, name):
        self.name = name

    def set_country_code(self, country_code):
        self.country_code = country_code

    def get_country_code(self):
        if isinstance(self.country_code, basestring):
            return str(self.country_code)
        else:
            return None

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

    def set_last_teleport(self):
        self.last_teleport = time()

    def set_coordinates(self, location_object):
        self.pos_x = location_object.tele_x
        self.pos_y = location_object.tele_y
        self.pos_z = location_object.tele_z
        return True

    def is_responsive(self):
        if self.health is not 0 and (isinstance(self.pos_x, float) and isinstance(self.pos_z, float)):
            return True
        else:
            return False

    def is_dead(self):
        if self.health == 0:
            return True
        else:
            return False

    def set_muted(self, flag):
        self.is_muted = flag
