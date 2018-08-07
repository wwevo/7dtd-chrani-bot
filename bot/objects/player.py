from time import time
import bot.external.flask_login as flask_login


class Player(flask_login.UserMixin):
    id = long
    name = str
    permission_levels = list

    pos_x = float
    pos_y = float
    pos_z = float

    rot_x = float
    rot_y = float
    rot_z = float

    old_rot_x = float
    old_rot_y = float
    old_rot_z = float

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
    blacklisted = bool
    authenticated = bool
    is_muted = bool
    is_online = bool
    last_teleport = int
    last_responsive = float
    initialized = bool

    playerfriends_list = list
    poll_listplayerfriends_lastpoll = float

    def get_id(self):
        return unicode(self.steamid)

    def __init__(self, **kwargs):
        self.last_teleport = 0
        self.is_muted = False
        self.is_online = False
        self.permission_levels = []
        self.last_responsive = time()
        self.entityid = None
        self.authenticated = False
        self.initialized = False
        self.ip = None
        self.id = None
        self.ping = None
        self.region = None
        self.country_code = None
        self.blacklisted = False

        self.playerfriends_list = []
        self.poll_listplayerfriends_lastpoll = 0

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
        if "authenticated" in level_list:
            self.set_authenticated(True)
        else:
            self.set_authenticated(False)

    def add_permission_level(self, level):
        if level not in self.permission_levels:
            self.permission_levels.append(level)
            if level == "authenticated":
                self.set_authenticated(True)

    def has_permission_level(self, level):
        if level in self.permission_levels:
            return True

    def remove_permission_level(self, level):
        if level in self.permission_levels:
            self.permission_levels.remove(level)
            if len(self.permission_levels) == 0 or level == "authenticated":
                self.set_authenticated(False)

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
            self.initialized = False
            return False

    def is_blacklisted(self):
        if self.blacklisted is True:
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
