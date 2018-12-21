from time import time
import datetime
import flask_login


class Player(flask_login.UserMixin):
    id = long
    name = str
    permission_levels = list
    is_allowed_to_chat = str

    pos_x = float
    pos_y = float
    pos_z = float

    old_pos_x = float
    old_pos_y = float
    old_pos_z = float

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

    is_online = bool
    is_banned = bool
    is_about_to_be_kicked = bool

    is_to_be_obliterated = bool

    is_logging_in = bool

    last_teleport = int
    last_responsive = float
    last_seen = float
    initialized = bool

    playerfriends_list = list
    poll_listplayerfriends_lastpoll = float
    active_teleport_thread = bool

    def get_id(self):
        return unicode(self.steamid)

    def __init__(self, **kwargs):
        self.health = 0
        self.last_teleport = 0
        self.last_seen = 0

        self.is_online = False
        self.is_banned = False
        self.is_manually_muted = False  # if the player got manually muted!
        self.is_allowed_to_chat = "None"  # if the player is allowed to chat

        self.is_about_to_be_kicked = False
        self.is_logging_in = False
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
        self.is_to_be_obliterated = False
        self.active_teleport_thread = False
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0

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

    def get_permission_levels_dict(self, permissions_list):
        permission_levels_dict = {}
        for permission_level in permissions_list:
            if permission_level not in self.permission_levels:
                permission_levels_dict[permission_level] = False
            else:
                permission_levels_dict[permission_level] = True

        return permission_levels_dict

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
        if self.is_to_be_obliterated is False and self.is_dead() is False and self.is_online is True:
            return True
        else:
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

    def get_last_seen(self):
        if self.last_seen == 0:
            readable_last_seen = "not available"
        else:
            readable_last_seen = datetime.datetime.utcfromtimestamp(self.last_seen).strftime("%Y-%m-%d %H:%M:%S")

        return readable_last_seen
