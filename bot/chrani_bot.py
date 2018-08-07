from bot.external.flask import request
from threading import *
import re
import time
import datetime
import math
from collections import deque

from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred

import bot.actions
import bot.observers

from bot.modules.settings import Settings
from bot.modules.locations import Locations
from bot.modules.webinterface.webinterface import Webinterface
from bot.modules.permissions import Permissions
from bot.objects.player import Player
from bot.modules.players import Players
from bot.modules.telnet_connection import TelnetConnection
from bot.modules.whitelist import Whitelist


class ChraniBot:
    app_root = str
    name = str
    bot_version = str

    time_launched = float
    time_running = float
    uptime = str
    is_active = bool  # used for restarting the bot safely after connection loss
    is_paused = bool  # used to pause all processing without shutting down the bot

    match_types = dict
    match_types_system = dict

    tn = object  # telnet connection to use for everything except player-actions and player-poll
    poll_tn = object
    telnet_lines_list = deque

    listlandprotection_interval = int
    listplayers_interval = int

    chat_colors = dict
    passwords = dict
    api_key = str
    banned_countries_list = list

    settings_dict = dict
    server_settings_dict = dict

    active_player_threads_dict = dict  # contains link to the players observer-thread
    landclaims_dict = dict

    players = object
    locations = object
    whitelist = object
    webinterface = object
    permission = object
    settings = object

    observers_list = list
    actions_list = list

    def __init__(self):
        self.paused = False
        self.settings = Settings()
        self.time_launched = time.time()
        self.time_running = 0
        self.uptime = "not available"

        self.name = self.settings.get_setting_by_name('bot_name')
        logger.info("{} started".format(self.name))

        self.tn = TelnetConnection(self, self.settings.get_setting_by_name('telnet_ip'), self.settings.get_setting_by_name('telnet_port'), self.settings.get_setting_by_name('telnet_password'), show_log_init=True)
        self.poll_tn = TelnetConnection(self, self.settings.get_setting_by_name('telnet_ip'), self.settings.get_setting_by_name('telnet_port'), self.settings.get_setting_by_name('telnet_password'))

        self.actions_list = bot.actions.actions_list
        self.observers_list = bot.observers.observers_list

        self.players = Players()  # players will be loaded on a need-to-load basis

        self.active_player_threads_dict = {}
        self.landclaims_dict = {}

        self.listplayers_interval = 1.5
        self.listplayers_interval_idle = self.listplayers_interval * 10

        self.listlandprotection_interval = 45

        self.whitelist = Whitelist()
        if self.settings.get_setting_by_name('whitelist_active') is not False:
            self.whitelist.activate()

        self.locations = Locations()

        self.passwords = {
            "authenticated": self.settings.get_setting_by_name('authentication_pass'),
            "donator": self.settings.get_setting_by_name('donator_pass'),
            "mod": self.settings.get_setting_by_name('mod_pass'),
            "admin": self.settings.get_setting_by_name('admin_pass')
        }

        self.permission_levels_list = ['admin', 'mod', 'donator', 'authenticated']
        self.permissions = Permissions(self.actions_list, self.permission_levels_list)

        self.load_from_db()

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
            # 'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: '(?P<player_name>.*)': /(?P<command>.+)",
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
            'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",
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
            'telnet_player_connected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*), entityid=(?P<entity_id>.*), name=(?P<player_name>.*), steamid=(?P<player_id>.*), steamOwner=(?P<owner_id>.*), ip=(?P<player_ip>.*)"
        }

        self.banned_countries_list = ['CN', 'CHN', 'KP', 'PRK', 'RU', 'RUS', 'NG', 'NGA']

        webinterface_thread_stop_flag = Event()
        webinterface_thread = Webinterface(webinterface_thread_stop_flag, self)  # I'm passing the bot (self) into it to have easy access to it's variables
        webinterface_thread.name = self.name + " webinterface"  # nice to have for the logs
        webinterface_thread.isDaemon()
        webinterface_thread.start()
        self.webinterface = webinterface_thread

    def load_from_db(self):
        self.settings.load_all()
        self.players.load_all()
        self.locations.load_all()  # load all location data to memory
        self.whitelist.load_all()  # load all whitelisted players
        self.permissions.load_all()  # get the permissions or create new permissions-file

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

            lcb_dict.update({m.group("player_steamid"): keystone_list})

        return lcb_dict

    def get_game_preferences(self):
        game_preferences_dict = {}
        game_preferences = self.tn.get_game_preferences()
        logger.debug(game_preferences)

        for m in re.finditer(self.match_types_system["getgameprefs_result_regexp"], self.tn.get_game_preferences()):
            game_preferences_dict.update({
                "Server-Port": m.group("server_port").rstrip(),
                "Server-IP": m.group("server_ip").rstrip()
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
        distance = math.floor(41 / 2) + 20 # (landclaim size / 2) + Deadzone
        start_coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)

        bases_near_list = self.locations.find_by_distance(start_coords, distance, "home")
        landclaims_near_list = self.landclaims_find_by_distance(start_coords, distance)

        clean_bases_near_list = []
        for base in bases_near_list:
            if base.keys()[0] != player_object.steamid:
                clean_bases_near_list.append(base)

        clean_landclaims_near_list = []
        for landclaim in landclaims_near_list:
            if str(landclaim.keys()[0]) != player_object.steamid:
                clean_landclaims_near_list.append(landclaim)

        return clean_bases_near_list, clean_landclaims_near_list

    def run(self):
        self.server_settings_dict = self.get_game_preferences()

        self.tn.togglechatcommandhide("/")

        listplayers_dict = {}
        listplayers_timeout_start = 0
        listplayers_interval = self.listplayers_interval

        listlandprotection_timeout_start = 0
        listlandprotection_interval = self.listlandprotection_interval

        self.telnet_lines_list = deque()

        self.is_active = True  # this is set so the main loop can be started / stopped
        while self.is_active:
            time_running_seconds = int(time.time() - self.time_launched)
            self.time_running = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=time_running_seconds)
            self.uptime = "{}d, {}h{}m{}s".format(self.time_running.day-1, self.time_running.hour, self.time_running.minute, self.time_running.second)

            if self.is_paused is True:
                time.sleep(1)
                continue

            if timeout_occurred(listlandprotection_interval, listlandprotection_timeout_start):
                self.landclaims_dict = self.poll_lcb()
                listlandprotection_timeout_start = time.time()

            if timeout_occurred(listplayers_interval, listplayers_timeout_start):
                if len(listplayers_dict) == 0:  # adjust poll frequency when the server is empty
                    listplayers_interval = self.listplayers_interval_idle
                else:
                    listplayers_interval = self.listplayers_interval

                listplayers_dict = self.players.manage_online_players(self, listplayers_dict)
                listplayers_timeout_start = time.time()

            """ since telnet_lines can contain one or more actual telnet lines, we add them to a queue and pop one line at a time.
            I hope to minimize the risk of a clogged bot this way, it might result in laggy commands. I shall have to monitor that """
            try:
                telnet_lines = self.tn.read_line()
            except Exception as e:
                logger.exception(e)
                raise IOError

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

                """ send telnet_line to player-thread
                check 'chat' telnet-line(s) for any known playername currently online
                """
                for player_steamid, player_object in self.players.players_dict.iteritems():
                    possible_action_for_player = re.search(player_object.name, telnet_line)
                    if possible_action_for_player:
                        if player_steamid in self.active_player_threads_dict:
                            active_player_thread = self.active_player_threads_dict[player_steamid]
                            active_player_thread["thread"].trigger_action_by_telnet(telnet_line)

                # handle playerspawns
                m = re.search(self.match_types_system["telnet_events_playerspawn"], telnet_line)
                if m:
                    try:
                        player_id = m.group("player_id")
                        command = m.group("command")
                        player_object = self.players.load(player_id)
                        active_player_thread = self.active_player_threads_dict[player_id]
                        active_player_thread["thread"].trigger_action(player_object, command)
                    except KeyError:
                        pass

                # telnet_player_connected is the earliest usable player-data line available, perfect spot to fire off triggers for whitelist and blacklist and such
                m = re.search(self.match_types_system["telnet_player_connected"], telnet_line)
                if m:
                    try:
                        player_id = m.group("player_id")
                        player_object = self.players.load(player_id)
                    except KeyError:
                        # no available player on record. we need to create a minimized dataset to be able to make use
                        # of the the existing observer approach. Since the observers are built to run within the scope
                        # of the player_ovserver script, we need to add the created player_object
                        player_dict = {
                            'entityid': int(m.group("entity_id")),
                            'steamid': m.group("player_id"),
                            'name': m.group("player_name"),
                            'ip': m.group("player_ip"),
                        }
                        player_object = Player(**player_dict)

                    logger.info("found player '{}' in the stream, accessing matrix...".format(player_object.name))
                    command_queue = []
                    for observer in self.observers_list:
                        if observer["type"] == 'trigger':  # we only want the triggers here
                            observer_function_name = observer["action"]
                            observer_parameters = eval(observer["env"])  # yes. Eval. It's my own data, chill out!
                            command_queue.append({
                                "action": observer_function_name,
                                "command_parameters": observer_parameters
                            })

                    for command in command_queue:
                        if isinstance(command["command_parameters"], tuple):
                            if len(command["command_parameters"]) > 1:
                                command["action"](*command["command_parameters"])
                            else:
                                command["action"](command["command_parameters"])

            time.sleep(0.1)  # to limit the speed a bit ^^

    def shutdown(self):
        self.tn.say("bot is shutting down...", color=self.chat_colors['warning'])
        self.is_active = False
        for player_steamid in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_steamid]
            active_player_thread["thread"].stopped.set()

        self.active_player_threads_dict.clear()
        self.telnet_lines_list = None
        self.tn.say("...bot has shut down!", color=self.chat_colors['success'])
        self.tn.tn.close()

        try:
            func = request.environ.get('werkzeug.server.shutdown')
            func()
        except RuntimeError:
            pass

        self.webinterface.stopped.set()


