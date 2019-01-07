import __main__  # my ide throws a warning here, but it works oO
import time
import datetime
import flask_login


class Player(flask_login.UserMixin):
    positional_data_timestamp = float

    id = long
    name = str
    permission_levels = list
    is_allowed_to_chat = str
    steamid = str
    entityid = str
    region = str
    country_code = str
    authenticated = bool
    is_banned = bool
    is_muted = bool
    last_teleport = int
    last_responsive = float
    last_seen = float
    playerfriends_list = list

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
    ip = str
    ping = int
    blacklisted = bool

    is_online = bool
    is_to_be_obliterated = bool
    is_logging_in = bool
    is_initialized = bool

    poll_listplayerfriends_lastpoll = float
    active_teleport_thread = bool

    def get_id(self):
        return unicode(self.steamid)

    def __init__(self, **kwargs):
        self.positional_data_timestamp = 0
        self.health = 0
        self.last_teleport = 0
        self.last_seen = 0

        self.is_online = False
        self.is_banned = False
        self.is_muted = False  # if the player got manually muted!
        self.is_allowed_to_chat = "None"  # if the player is allowed to chat

        self.is_logging_in = False
        self.permission_levels = []
        self.last_responsive = time.time()
        self.entityid = None
        self.authenticated = False
        self.is_initialized = False
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

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def set_name(self, name):
        chrani_bot = __main__.chrani_bot
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["name"] = name

    def set_country_code(self, country_code):
        chrani_bot = __main__.chrani_bot
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["country_code"] = country_code

    def get_country_code(self):
        chrani_bot = __main__.chrani_bot
        if isinstance(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("country_code"), basestring):
            return str(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("country_code"))
        else:
            return None

    def set_authenticated(self, authenticated):
        chrani_bot = __main__.chrani_bot
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["authenticated"] = authenticated
        return True

    def get_permission_levels_dict(self, permissions_list):
        chrani_bot = __main__.chrani_bot
        permission_levels_dict = {}
        for permission_level in permissions_list:
            if permission_level not in chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("permission_levels", []):
                permission_levels_dict[permission_level] = False
            else:
                permission_levels_dict[permission_level] = True

        return permission_levels_dict

    def set_permission_levels(self, level_list):
        chrani_bot = __main__.chrani_bot
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["permission_levels"] = level_list
        if "authenticated" in level_list:
            self.set_authenticated(True)
        else:
            self.set_authenticated(False)

    def add_permission_level(self, level):
        chrani_bot = __main__.chrani_bot
        if level not in chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("permission_levels", []) and self.name != "system":
            chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("permission_levels").append(level)
            if level == "authenticated":
                self.set_authenticated(True)

    def has_permission_level(self, level=None):
        chrani_bot = __main__.chrani_bot
        if level in chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("permission_levels", []):
            return True

    def remove_permission_level(self, level):
        chrani_bot = __main__.chrani_bot
        if level in chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("permission_levels"):
            chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("permission_levels").remove(level)
            if len(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("permission_levels")) == 0 or level == "authenticated":
                self.set_authenticated(False)

    def set_last_teleport(self, coord_tuple):
        chrani_bot = __main__.chrani_bot
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["pos_x"] = coord_tuple[0]
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["pos_y"] = coord_tuple[1]
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["pos_z"] = coord_tuple[2]
        chrani_bot.dom["bot_data"]["player_data"][self.steamid]["last_teleport"] = time.time()

    def get_coord_tuple(self):
        chrani_bot = __main__.chrani_bot
        coord_tuple = (
            chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_x", 0),
            chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_y", 0),
            chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_z", 0)
        )
        return coord_tuple

    def get_position_string(self):
        chrani_bot = __main__.chrani_bot
        position_string = "{pos_x} {pos_y} {pos_z}".format(
            pos_x=int(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("pos_x", 0)),
            pos_y=int(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("pos_y", 0)),
            pos_z=int(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("pos_z", 0))
        )
        return position_string

    def is_responsive(self):
        chrani_bot = __main__.chrani_bot
        if chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("is_to_be_obliterated", False) is False and self.is_dead() is False and chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("is_online") is True:
            return True
        else:
            return False

    def is_blacklisted(self):
        chrani_bot = __main__.chrani_bot
        if chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("blacklisted") is True:
            return True
        else:
            return False

    def is_dead(self):
        chrani_bot = __main__.chrani_bot
        if chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("health") == 0:
            return True
        else:
            return False

    def get_last_seen(self):
        chrani_bot = __main__.chrani_bot
        if chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid, {}).get("last_seen", 0) == 0:
            readable_last_seen = "not available"
        else:
            readable_last_seen = datetime.datetime.utcfromtimestamp(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("last_seen")).strftime("%Y-%m-%d %H:%M:%S")

        return readable_last_seen

    def get_leaflet_marker_json(self):
        chrani_bot = __main__.chrani_bot
        player_list = []
        if not isinstance(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_x"), float) or not isinstance(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_y"), float) or not isinstance(chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_z"), float):
            return player_list

        player_dict = {
            "id": "{}".format(self.steamid),
            "owner": self.steamid,
            "identifier": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("name"),
            "name": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("self.name"),
            "radius": 3,
            "pos_x": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_x"),
            "pos_y": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_y"),
            "pos_z": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("pos_z"),
            "online": chrani_bot.dom.get("bot_data").get("player_data").get(self.steamid).get("is_online"),
            "shape": "icon",
            "type": "icon",
            "layerGroup": "players"
        }

        return player_dict
