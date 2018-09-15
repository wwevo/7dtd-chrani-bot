from threading import *
import re
import time
import datetime
import math
import sys
import os
from collections import deque
from threading import Event

from bot.player_observer import PlayerObserver
from bot.objects.player import Player
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred

import bot.actions as actions
import bot.observers as observers

from bot.modules.settings import Settings
from bot.modules.locations import Locations
from bot.modules.permissions import Permissions
from bot.modules.players import Players
from bot.modules.telnet_connection import TelnetConnection
from bot.modules.whitelist import Whitelist


class ChraniBot(Thread):
    app_root = str
    name = str
    bot_version = str

    app = object
    flask = object
    flask_login = object
    socketio = object

    time_launched = float
    time_running = float
    oberservers_execution_time = float
    uptime = str
    is_active = bool  # used for restarting the bot safely after connection loss
    is_paused = bool  # used to pause all processing without shutting down the bot
    has_connection = bool  # used to pause all processing without shutting down the bot
    initiate_shutdown = bool

    match_types = dict
    match_types_system = dict

    tn = object  # telnet connection to use for everything except player-actions and player-poll
    poll_tn = object
    telnet_lines_list = deque

    listlandprotection_interval = int
    listplayers_interval = int
    restart_delay = int

    chat_colors = dict
    passwords = dict
    api_key = str
    banned_countries_list = list

    settings_dict = dict
    server_settings_dict = dict

    active_player_threads_dict = dict  # contains link to the players observer-thread
    landclaims_dict = dict

    actions = object
    players = object
    locations = object
    whitelist = object
    webinterface = object
    permission = object
    settings = object

    observers_list = list
    actions_list = list

    def __init__(self, event, app, flask, flask_login, socketio):
        self.app = app
        self.flask = flask
        self.flask_login = flask_login
        self.socketio = socketio
        self.is_paused = False
        self.has_connection = False
        self.settings = Settings()
        self.time_launched = time.time()
        self.time_running = 0
        self.uptime = "not available"
        self.initiate_shutdown = False
        self.oberservers_execution_time = 0.0
        self.restart_delay = 0

        self.name = self.settings.get_setting_by_name('bot_name')
        logger.info("{} started".format(self.name))

        self.actions = actions
        self.actions_list = actions.actions_list
        self.observers_list = observers.observers_list

        self.players = Players()  # players will be loaded on a need-to-load basis

        self.active_player_threads_dict = {}
        self.landclaims_dict = {}

        self.listplayers_interval = 1.5
        self.listplayers_interval_idle = self.listplayers_interval * 10

        self.listlandprotection_interval = 15

        self.whitelist = Whitelist()
        if self.settings.get_setting_by_name('whitelist_active') is not False:
            self.whitelist.activate()

        self.locations = Locations()

        self.passwords = self.settings.get_setting_by_name('authentication_groups')

        self.permission_levels_list = self.passwords.keys()  # ['admin', 'mod', 'donator', 'authenticated']
        self.permissions = Permissions(self.actions_list, self.permission_levels_list)

        self.chat_colors = {
            "standard": "ffffff",
            "info": "4286f4",
            "success": "00ff04",
            "error": "8c0012",
            "warning": "ffbf00",
            "alert": "ba0085",
            "background": "cccccc",
        }

        self.match_types = {
            # matches any command a player issues in game-chat
            'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF (GameMessage handled by mod ('Coppis command additions'|'Coppis command additions Light'): Chat| Chat): '(?P<player_name>.*)': /(?P<command>.*)",
            # player joined / died messages etc
            'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*): (?P<steamid>\d+)",
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)"
        }

        self.match_types_system = {
            # captures the response for telnet commands. used for example to capture teleport response
            'telnet_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command\s'(?P<telnet_command>.*)'\s((?P<source>by Telnet|from client))\s(?(source)from(?P<ip>.*):(?P<port>.*)|(?P<player_steamid>.*))",
            # the game logs several player-events with additional information (for now i only capture the one i need, but there are several more useful ones
            'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), position: (?P<pos_x>.*), (?P<pos_y>.*), (?P<pos_z>.*)\): EntityID=(?P<entity_id>.*), PlayerID='(?P<player_id>.*)', OwnerID='(?P<owner_steamid>.*)', PlayerName='(?P<player_name>.*)'",
            # isolates the disconnected log entry to get the total session time of a player easily
            'telnet_player_playtime': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",
            # to parse the telnets listplayers response
            'listplayers_result_regexp': r"\d{1,2}. id=(\d+), (.+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(.*), ping=(\d+)\r\n",
            # to parse the telnets listlandprotection response
            'listlandprotection_result_regexp': r"Player \"(?:.+)\((?P<player_steamid>\d+)\)\" owns \d+ keystones \(.+\)\s(?P<keystones>(\s+\(.+\)\s){1,})",
            # to parse the telnets listlandplayerfriends response
            'listplayerfriends_result_regexp': r"FriendsOf id=(?P<player_steamid>([0-9]{17})), friends=(?P<friendslist>([0-9,]{17,}))",
            # to parse the telnets getgameprefs response
            'getgameprefs_result_regexp': r"GamePref\.ConnectToServerIP = (?P<server_ip>.*)\nGamePref\.ConnectToServerPort = (?P<server_port>.*)\n",
            # player joined / died messages
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)",
            # pretty much the first usable line during a players login
            # 'eac_register_client': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF \[EAC\] Log: \[RegisterClient\] Client: (?P<client>.*) PlayerGUID: (?P<player_id>.*) PlayerIP: (?P<player_ip>.*) OwnerGUID: (?P<owner_id>.*) PlayerName: (?P<player_name>.*)",
            # player is 'valid' from here on
            # 'eac_successful': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF EAC authentication successful, allowing user: EntityID=(?P<entitiy_id>.*), PlayerID='(?P<player_id>.*)', OwnerID='(?P<owner_id>.*)', PlayerName='(?P<player_name>.*)'"
            'telnet_player_connected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*), entityid=(?P<entity_id>.*), name=(?P<player_name>.*), steamid=(?P<player_id>.*), steamOwner=(?P<owner_id>.*), ip=(?P<player_ip>.*)",
            'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*): EntityID=(?P<entity_id>.*), PlayerID='(?P<player_id>.*)', OwnerID='(?P<owner_id>.*)', PlayerName='(?P<player_name>.*)'",
            'screamer_spawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF (?P<command>.+?) \[type=(.*), name=(?P<zombie_name>.+?), id=(?P<entity_id>.*)\] at \((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\) Day=(\d.*) TotalInWave=(\d.*) CurrentWave=(\d.*)"
        }

        self.banned_countries_list = self.settings.get_setting_by_name('banned_countries')
        self.stopped = event
        Thread.__init__(self)

    def load_from_db(self):
        self.settings.load_all()
        self.players.load_all()
        self.locations.load_all()  # load all location data to memory
        self.whitelist.load_all()  # load all whitelisted players
        self.permissions.load_all()  # get the permissions or create new permissions-file

    def start_player_thread(self, player_object):
        player_observer_thread_stop_flag = Event()
        player_observer_thread = PlayerObserver(player_observer_thread_stop_flag, self, player_object.steamid)  # I'm passing the bot (self) into it to have easy access to it's variables
        player_observer_thread.name = player_object.steamid  # nice to have for the logs
        player_observer_thread.isDaemon()
        player_observer_thread.start()
        self.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
        self.socketio.emit('update_leaflet_markers', self.players.get_leaflet_marker_json([player_object]), namespace='/chrani-bot/public')
        self.active_player_threads_dict.update({player_object.steamid: {"event": player_observer_thread_stop_flag, "thread": player_observer_thread}})

    def poll_lcb(self):
        lcb_dict = {}
        test_str = self.tn.listlandprotection()

        # I can't believe what a bitch this thing was. I tried no less than eight hours to find this crappy solution
        # re could not find a match whenever any form of unicode was present.  I've tried converting, i've tried sting declarations,
        # I've tried flags. Something was always up. This is the only way i got this working.
        try:
            unicode(test_str, "ascii")
        except UnicodeError:
            test_str = unicode(test_str, "utf-8")
        else:
            pass

        # horrible, horrible way. But it works for now!
        for m in re.finditer(self.match_types_system["listlandprotection_result_regexp"], test_str):
            keystones = re.findall(r"\((?P<pos_x>.\d{1,5}),\s(?P<pos_y>.\d{1,5}),\s(?P<pos_z>.\d{1,5})", m.group("keystones"))
            keystone_list = []
            for keystone in keystones:
                keystone_list.append(keystone)

            try:
                target_player = self.players.get_by_steamid(m.group("player_steamid"))
            except KeyError:
                continue

            lcb_dict.update({target_player.steamid: keystone_list})

        return lcb_dict

    def get_lcb_marker_json(self, lcb_dict):
        lcb_list_final = []
        server_settings = self.server_settings_dict
        try:
            land_claim_size = server_settings["LandClaimSize"]
        except TypeError:
            return lcb_list_final

        for lcb_owner, lcb_list in lcb_dict.iteritems():
            for lcb in lcb_list:
                lcb_list_final.append({
                    "id": "{}_lcb_{}{}{}".format(str(lcb_owner), str(lcb[0]), str(lcb[1]), str(lcb[2])),
                    "owner": str(lcb_owner),
                    "identifier": "{}_lcb_{}{}{}".format(str(lcb_owner), str(lcb[0]), str(lcb[1]), str(lcb[2])),
                    "name": str(lcb_owner),
                    "radius": int(land_claim_size),
                    "inner_radius": 3,
                    "pos_x": int(lcb[0]),
                    "pos_y": int(lcb[1]),
                    "pos_z": int(lcb[2]),
                    "type": "square",
                    "layerGroup": "landclaims"
                })

        return lcb_list_final

    def get_game_preferences(self):
        game_preferences = self.tn.get_game_preferences()
        logger.debug(game_preferences)

        game_preferences_dict = {}
        for key, value in game_preferences:
            game_preferences_dict.update({
                key: value
            })

        return game_preferences_dict

    def landclaims_find_by_distance(self, start_coords, distance_in_blocks):
        landclaims_in_reach_list = []
        landclaims_dict = self.landclaims_dict
        for player_steamid, landclaims in landclaims_dict.iteritems():
            for landclaim in landclaims:
                distance = math.sqrt((float(landclaim[0]) - float(start_coords[0]))**2 + (float(landclaim[1]) - float(start_coords[1]))**2 + (float(landclaim[2]) - float(start_coords[2]))**2)
                if distance < distance_in_blocks:
                    landclaims_in_reach_list.append({player_steamid: landclaim})

        return landclaims_in_reach_list

    def check_for_homes(self, player_object):
        distance = math.floor(41 / 2) + 20  # (landclaim size / 2) + Deadzone
        start_coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)

        bases_near_list = self.locations.find_by_distance(start_coords, distance, "home")
        landclaims_near_list = self.landclaims_find_by_distance(start_coords, distance)

        clean_bases_near_list = []
        for base in bases_near_list:
            if base.owner != player_object.steamid:
                clean_bases_near_list.append(base)

        clean_landclaims_near_list = []
        for landclaim in landclaims_near_list:
            if str(landclaim.keys()[0]) != player_object.steamid:
                clean_landclaims_near_list.append(landclaim)

        return clean_bases_near_list, clean_landclaims_near_list

    def on_screamer_spawn(self, m):
        try:
            entity_id = m.group("entity_id")
            pos_x = m.group("pos_x")
            pos_y = m.group("pos_y")
            pos_z = m.group("pos_z")
            command = m.group("command")
            zombie_name = m.group("zombie_name")
            player_object = self.players.get_by_steamid('system')
            if command == "Spawned" and zombie_name == "zombieScreamer":
                villages = self.locations.find_by_type('village')
                for village in villages:
                    if village.position_is_inside_boundary((pos_x,pos_y, pos_z)):
                        self.actions.common.trigger_action(self, player_object, player_object, "screamer spawned inside village {}".format(entity_id))
        except KeyError:
            pass

    def run(self):
        self.load_from_db()

        listplayers_dict = {}
        listplayers_timeout_start = 0
        listplayers_interval = self.listplayers_interval

        listlandprotection_timeout_start = 0
        listlandprotection_interval = self.listlandprotection_interval

        update_status_timeout_start = 0
        update_status_interval = self.listplayers_interval * 2

        self.telnet_lines_list = deque()

        self.is_active = True  # this is set so the main loop can be started / stopped
        while self.is_active or not self.stopped:
            try:
                time_running_seconds = int(time.time() - self.time_launched)

                if self.initiate_shutdown is True:
                    self.shutdown()
                    continue

                if timeout_occurred(listplayers_interval, listplayers_timeout_start):
                    if len(listplayers_dict) == 0:  # adjust poll frequency when the server is empty
                        listplayers_interval = self.listplayers_interval_idle
                    else:
                        listplayers_interval = self.listplayers_interval

                    listplayers_dict = self.players.manage_online_players(self)
                    listplayers_timeout_start = time.time()

                if self.is_paused and self.has_connection:
                    time.sleep(self.listplayers_interval)
                    continue

                """ since telnet_lines can contain one or more actual telnet lines, we add them to a queue and pop one line at a time.
                I hope to minimize the risk of a clogged bot this way, it might result in laggy commands. I shall have to monitor that """
                try:
                    telnet_lines = self.tn.read_line()
                except AttributeError:
                    raise IOError

                if timeout_occurred(update_status_interval, update_status_timeout_start):
                    self.time_running = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=time_running_seconds)
                    self.uptime = "{}d, {}h{}m".format(self.time_running.day-1, self.time_running.hour, self.time_running.minute)
                    self.socketio.emit('server_online', '', namespace='/chrani-bot/public')
                    self.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
                    update_status_timeout_start = time.time()
                    execution_time = 0.0
                    count = 0
                    for player_steamid, player_thread in self.active_player_threads_dict.iteritems():
                        count = count + 1
                        execution_time += player_thread["thread"].last_execution_time
                    if count > 0:
                        self.oberservers_execution_time = execution_time / count

                if timeout_occurred(listlandprotection_interval, listlandprotection_timeout_start):
                    if len(listplayers_dict) > 0 or not self.landclaims_dict:
                        polled_lcb = self.poll_lcb()
                        lcb_owners_to_delete = {}
                        lcb_owners_to_update = {}
                        lcb_owners_to_update.update(polled_lcb)
                        for lcb_widget_owner in lcb_owners_to_update.keys():
                            try:
                                player_object = self.players.get_by_steamid(lcb_widget_owner)
                            except KeyError:
                                continue

                            self.socketio.emit('refresh_player_lcb_widget', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')

                        self.socketio.emit('update_leaflet_markers', self.get_lcb_marker_json(lcb_owners_to_update), namespace='/chrani-bot/public')
                        self.socketio.emit('remove_leaflet_markers', self.get_lcb_marker_json(lcb_owners_to_delete), namespace='/chrani-bot/public')
                        self.landclaims_dict = polled_lcb

                    listlandprotection_timeout_start = time.time()

                if telnet_lines is not None:
                    for line in telnet_lines:
                        self.telnet_lines_list.append(line)  # get the current global telnet-response

                try:
                    telnet_line = self.telnet_lines_list.popleft()
                except IndexError:
                    telnet_line = None

                if telnet_line is not None:
                    m = re.search(self.match_types_system["telnet_commands"], telnet_line)
                    if not m or m and m.group('telnet_command') != 'lp' and m.group('telnet_command') != 'llp2':
                        if telnet_line != '':
                            logger.debug(telnet_line)

                    # handle playerspawns
                    m = re.search(self.match_types_system["telnet_player_connected"], telnet_line)
                    if m:
                        connecting_player = self.players.player_entered_telnet(m)
                        connecting_player.thread.trigger_action(connecting_player.player_object, "entered the stream")

                    m = re.search(self.match_types_system["telnet_events_playerspawn"], telnet_line)
                    if m:
                        spawning_player = self.players.player_entered_the_world(m)
                        spawning_player.thread.trigger_action(spawning_player.player_object, "entered the world")

                    # handle other spawns
                    # r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Spawned \[type=(.*), name=zombieScreamer, id=(?P<entity_id>.*)\] at \((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\) Day=(\d.*) TotalInWave=(\d.*) CurrentWave=(\d.*)"
                    m = re.search(self.match_types_system["screamer_spawn"], telnet_line)
                    if m:
                        self.on_screamer_spawn(m)

                    """ send telnet_line to player-thread
                    check 'chat' telnet-line(s) for any known playername currently online
                    """
                    for player_steamid, player_object in self.players.players_dict.iteritems():
                        possible_action_for_player = re.search(re.escape(player_object.name), telnet_line)
                        if possible_action_for_player:
                            if player_steamid in self.active_player_threads_dict:
                                active_player_thread = self.active_player_threads_dict[player_steamid]
                                active_player_thread["thread"].trigger_action_by_telnet(telnet_line)

                time.sleep(0.125)  # to limit the speed a bit ^^

            except (IOError, NameError, AttributeError) as error:
                """ clean up bot to have a clean restart when a new connection can be established """
                log_message = "no telnet-connection - trying to connect..."

                try:
                    self.tn = TelnetConnection(self, self.settings.get_setting_by_name('telnet_ip'), self.settings.get_setting_by_name('telnet_port'), self.settings.get_setting_by_name('telnet_password'), show_log_init=True)
                    self.poll_tn = TelnetConnection(self, self.settings.get_setting_by_name('telnet_ip'), self.settings.get_setting_by_name('telnet_port'), self.settings.get_setting_by_name('telnet_password'))
                    self.has_connection = True
                    self.is_paused = False
                    self.server_settings_dict = self.get_game_preferences()
                    self.tn.togglechatcommandhide("/")
                except IOError as e:
                    self.socketio.emit('server_offline', '', namespace='/chrani-bot/public')
                    self.has_connection = False
                    self.is_paused = True
                    log_message = "{} - will try again in {} seconds ({} / {})".format(log_message, str(self.restart_delay), error, e)
                    logger.info(log_message)
                    # logger.exception(log_message)
                    time.sleep(self.restart_delay)
                    self.restart_delay = 20

    def shutdown(self):
        self.socketio.emit('server_offline', '', namespace='/chrani-bot/public')
        time.sleep(5)
        self.is_active = False
        for player_steamid in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_steamid]
            active_player_thread["thread"].stopped.set()

        self.active_player_threads_dict.clear()
        self.telnet_lines_list = None
        self.stopped.set()
        try:
            os._exit(0)
        except SystemExit:
            logger.info("bot has shut down!")