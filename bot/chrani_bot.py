import re
import sys
import time
from threading import Event
import json
from collections import deque

from bot.logger import logger
from bot.assorted_functions import byteify, timeout_occurred
from bot.actions_spawn import actions_spawn
from bot.actions_authentication import actions_authentication
from bot.actions_dev import actions_dev, observers_dev
from bot.actions_home import actions_home
from bot.actions_lobby import actions_lobby, observers_lobby
from bot.actions_locations import actions_locations, observers_locations
from bot.actions_whitelist import actions_whitelist, observers_whitelist
from bot.command_line_args import args_dict
from bot.locations import Locations
from bot.permissions import Permissions
from bot.player import Player
from bot.player_observer import PlayerObserver
from bot.players import Players
from bot.telnet_connection import TelnetConnection
from bot.whitelist import Whitelist


class ChraniBot:
    bot_name = str
    bot_version = str
    is_active = bool  # used for restarting the bot safely after connection loss

    match_types = dict
    match_types_system = dict
    banned_countries_list = list

    tn = object  # telnet connection to use for everything except player-actions and player-poll
    poll_tn = object
    telnet_lines_list = deque

    listplayers_interval = int
    chat_colors = dict
    passwords = dict
    api_key = str

    settings_dict = dict
    server_settings_dict = dict

    active_player_threads_dict = dict  # contains link to the players observer-thread

    players = object
    locations = object
    whitelist = object
    permission = object

    observers = list
    player_actions = list

    def load_bot_settings(self, prefix):
        filename = "data/configurations/{}.json".format(prefix)
        try:
            with open(filename) as file_to_read:
                settings_dict = byteify(json.load(file_to_read))
        except IOError:  # no settings file available
            settings_dict = None
        return settings_dict

    def __init__(self):
        self.settings_dict = self.load_bot_settings(args_dict['Database-file'])

        self.bot_name = self.settings_dict['bot_name']
        logger.info("{} started".format(self.bot_name))

        self.tn = TelnetConnection(self, self.settings_dict['telnet_ip'], self.settings_dict['telnet_port'], self.settings_dict['telnet_password'], show_log_init=True)
        self.poll_tn = TelnetConnection(self, self.settings_dict['telnet_ip'], self.settings_dict['telnet_port'], self.settings_dict['telnet_password'])

        self.player_actions = actions_spawn + actions_whitelist + actions_authentication + actions_locations + actions_home + actions_lobby + actions_dev
        self.observers = observers_whitelist + observers_dev + observers_lobby + observers_locations

        self.players = Players()  # players will be loaded on a need-to-load basis
        self.listplayers_interval = 1.5
        self.listplayers_interval_idle = self.listplayers_interval * 10
        self.active_player_threads_dict = {}

        self.locations = Locations()

        self.passwords = {
            "authenticated": 'openup',
            "donator": 'blingbling',
            "mod": 'hoopmeup',
            "admin": 'ecvrules'
        }

        self.whitelist = Whitelist()
        self.permission_levels_list = ['admin', 'mod', 'donator', 'authenticated', None]
        self.permissions = Permissions(self.player_actions, self.permission_levels_list)

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
            'chat_commands_coppi': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GameMessage handled by mod 'Coppis command additions': Chat: '(?P<player_name>.*)': /(?P<command>.*)",
            # player joined / died messages etc
            'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*): (?P<steamid>\d+)",
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)"
        }

        self.match_types_system = {
            # captures the response for telnet commands. used for example to capture teleport response
            'telnet_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command\s'(?P<telnet_command>.*)'\s((?P<source>by Telnet|from client))\s(?(source)from(?P<ip>.*):(?P<port>.*)|(?P<player_steamid>.*))",
            # the game logs several player-events with additional information (for now i only capture the one i need, but there are several more useful ones
            'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), position: (?P<pos_x>.*), (?P<pos_y>.*), (?P<pos_z>.*)\): EntityID=(?P<entity_id>.*), PlayerID='(?P<steamid>.*), OwnerID='(?P<owner_steamid>.*)', PlayerName='(?P<player_name>.*)'",
            # isolates the disconnected log entry to get the total session time of a player easily
            'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",
            # to parse the telnets listplayers response
            'listplayers_result_regexp': r"\d{1,2}. id=(\d+), (.+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(.*), ping=(\d+)\r\n",
            # to parse the telnets getgameprefs response
            'getgameprefs_result_regexp': r"GamePref\.ConnectToServerIP = (?P<server_ip>.*)\nGamePref\.ConnectToServerPort = (?P<server_port>.*)\n",
            # player joined / died messages
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)",
            # pretty much the first usable line during a players login
            #'eac_register_client': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF \[EAC\] Log: \[RegisterClient\] Client: (?P<client>.*) PlayerGUID: (?P<player_id>.*) PlayerIP: (?P<player_ip>.*) OwnerGUID: (?P<owner_id>.*) PlayerName: (?P<player_name>.*)",
            # player is 'valid' from here on
            #'eac_successful': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF EAC authentication successful, allowing user: EntityID=(?P<entitiy_id>.*), PlayerID='(?P<player_id>.*)', OwnerID='(?P<owner_id>.*)', PlayerName='(?P<player_name>.*)'"
            'telnet_player_connected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*), entityid=(?P<entitiy_id>.*), name=(?P<player_name>.*), steamid=(?P<player_id>.*), steamOwner=(?P<owner_id>.*), ip=(?P<player_ip>.*)"
        }

        self.banned_countries_list = ['CN', 'CHN', 'KP', 'PRK', 'RU', 'RUS', 'NG', 'NGA']

        self.server_settings_dict = self.get_game_preferences()

    def load_from_db(self):
        self.locations.load_all(store=True)  # load all location data to memory
        self.whitelist.load_all()  # load all whitelisted players
        self.permissions.load_all()  # get the permissions or create new permissions-file

    def shutdown_bot(self):
        self.shutdown()

        sys.exit()

    def poll_players(self):
        online_players_dict = {}
        for m in re.finditer(self.match_types_system["listplayers_result_regexp"], self.poll_tn.listplayers()):
            online_players_dict.update({m.group(16): {
                "id":       m.group(1),
                "name":     str(m.group(2)),
                "pos_x":    float(m.group(3)),
                "pos_y":    float(m.group(4)),
                "pos_z":    float(m.group(5)),
                "rot_x":    float(m.group(6)),
                "rot_y":    float(m.group(7)),
                "rot_z":    float(m.group(8)),
                "remote":   bool(m.group(9)),
                "health":   int(m.group(10)),
                "deaths":   int(m.group(11)),
                "zombies":  int(m.group(12)),
                "players":  int(m.group(13)),
                "score":    m.group(14),
                "level":    m.group(15),
                "steamid":  m.group(16),
                "ip":       str(m.group(17)),
                "ping":     int(m.group(18))
            }})
        return online_players_dict

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

    def run(self):
        self.is_active = True  # this is set so the main loop can be started / stopped
        self.tn.togglechatcommandhide("/")

        listplayers_dict = {}
        list_players_timeout_start = 0
        listplayers_interval = self.listplayers_interval
        telnet_line = None
        self.telnet_lines_list = deque()

        while self.is_active:
            if timeout_occurred(listplayers_interval, list_players_timeout_start):
                # get all currently online players and store them in a dictionary
                last_listplayers_dict = listplayers_dict
                listplayers_dict = self.poll_players()
                if len(listplayers_dict) == 0:  # adjust poll frequency
                    listplayers_interval = self.listplayers_interval_idle
                else:
                    listplayers_interval = self.listplayers_interval

                list_players_timeout_start = time.time()

                # prune players not online anymore
                for player in set(self.players.players_dict) - set(listplayers_dict.keys()):
                    del self.players.players_dict[player]

                # create new player entries / update existing ones
                for player_steamid, player_dict in listplayers_dict.iteritems():
                    try:
                        player_object = self.players.get(player_steamid)
                        # player is already online and needs updating
                        player_object.update(**player_dict)
                        if last_listplayers_dict != listplayers_dict:  # but only if they have changed at all!
                            """ we only update this if things have changed since this poll is slow and might
                            be out of date. Any teleport issued by the bot or a player would generate more accurate data
                            If it HAS changed it is by all means current and can be used to update the object.
                            """
                            self.players.upsert(player_object)
                    except KeyError:  # player has just come online
                        try:
                            player_object = self.players.load(player_steamid)
                            # player has a file on disc, update database!
                            player_object.update(**player_dict)
                            self.players.upsert(player_object)
                        except KeyError:  # player is totally new, create file!
                            player_object = Player(**player_dict)
                            self.players.upsert(player_object, save=True)
                    # there should be a valid object state here now ^^

                """ handle player-threads """
                for player_steamid, player_object in self.players.players_dict.iteritems():
                    """ start player_observer_thread for each player not already being observed """
                    if player_steamid not in self.active_player_threads_dict:
                        player_observer_thread_stop_flag = Event()
                        player_observer_thread = PlayerObserver(player_observer_thread_stop_flag, self, str(player_steamid))  # I'm passing the bot (self) into it to have easy access to it's variables
                        player_observer_thread.name = player_steamid  # nice to have for the logs
                        player_observer_thread.isDaemon()
                        player_observer_thread.trigger_action(player_object, "entered the stream")
                        player_observer_thread.start()
                        # self.players.upsert(player_object, save=True)
                        self.active_player_threads_dict.update({player_steamid: {"event": player_observer_thread_stop_flag, "thread": player_observer_thread}})

                for player_steamid in set(self.active_player_threads_dict) - set(self.players.players_dict.keys()):
                    """ prune all active_player_threads from players no longer online """
                    active_player_thread = self.active_player_threads_dict[player_steamid]
                    stop_flag = active_player_thread["thread"]
                    stop_flag.stopped.set()
                    del self.active_player_threads_dict[player_steamid]

            """ since telnet_lines can contain one or more actual telnet lines, we add them to a queue and pop one line at a time.
            I hope to minimize the risk of a clogged bot this way, it might result in laggy commands. I shall have to monitor that """
            try:
                telnet_lines = self.tn.read_line()
            except Exception as e:
                logger.error(e)
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
                if not m or m and m.group('telnet_command') != 'lp':
                    if telnet_line != '':
                        logger.debug(telnet_line)
                # this part might be obsolete now, it was for handling the black screen of death. i might have
                # found a simpler solution ^^
                #
                # if m:
                #     if m.group("telnet_command").startswith("tele"):
                #         c = re.search(r"^(tele|teleportplayer) (?P<player>.*) (?P<pos_x>.*) (?P<pos_y>.*) (?P<pos_z>.*)", m.group("telnet_command"))
                #         if c:
                #             for player_steamid, player_object in self.players.players_dict.iteritems():
                #                 if c.group("player") in [player_object.name, player_object.steamid]:
                #                     player_object.switch_off("main - teleportplayer")
                #
                # m = re.search(self.match_types_system["telnet_events_player_gmsg"], telnet_line)
                # if m:
                #     if m.group("command") == "died":
                #         for player_steamid, player_object in self.players.players_dict.iteritems():
                #             if player_object.name == m.group("player_name"):
                #                 if player_steamid in self.active_player_threads_dict:
                #                     player_object.switch_off("main - died")
                #
                #     if m.group("command") == "joined the game":
                #         for player_steamid, player_object in self.players.players_dict.iteritems():
                #             if player_object.name == m.group("player_name"):
                #                 if player_steamid in self.active_player_threads_dict:
                #                     if player_object.has_health() is True:
                #                         player_object.switch_on("main - joined the game")
                #
                # m = re.search(self.match_types_system["telnet_events_playerspawn"], telnet_line)
                # if m:
                #     if m.group("command") == "Died" or m.group("command") == "Teleport":
                #         for player_steamid, player_object in self.players.players_dict.iteritems():
                #             if player_object.name == m.group("player_name"):
                #                 try:
                #                     player_object.switch_on("main - respawned")
                #                 except KeyError:
                #                     pass

                """ send telnet_line to player-thread
                check 'chat' telnet-line(s) for any known playername currently online
                """
                for player_steamid, player_object in self.players.players_dict.iteritems():
                    possible_action_for_player = re.search(player_object.name, telnet_line)
                    if possible_action_for_player:
                        if player_steamid in self.active_player_threads_dict:
                            active_player_thread = self.active_player_threads_dict[player_steamid]
                            active_player_thread["thread"].trigger_action_by_telnet(telnet_line)

                """ work through triggers caused by telnet_activity """
                # telnet_player_connected is the earliest usable player-data line available, perfect spot to fire off triggers for whitelist and blacklist and such
                m = re.search(self.match_types_system["telnet_player_connected"], telnet_line)
                if m:
                    try:
                        player_object = self.players.load(m.group("player_id"))
                    except KeyError:
                        player_dict = {
                            'steamid': m.group("player_id"),
                            'name': m.group("player_name"),
                            'ip': m.group("player_ip")
                        }
                        player_object = Player(**player_dict)

                    logger.info("found player '{}' in the stream, accessing matrix...".format(player_object.name))
                    command_queue = []
                    for observer in self.observers:
                        if observer[0] == 'trigger':  # we only want the triggers here
                            observer_function_name = observer[2]
                            observer_parameters = eval(observer[3])  # yes. Eval. It's my own data, chill out!
                            command_queue.append([observer_function_name, observer_parameters])

                    for command in command_queue:
                        try:
                            command[0](*command[1])
                        except TypeError:
                            command[0](command[1])

            time.sleep(0.05)  # to limit the speed a bit ^^

    def shutdown(self):
        self.is_active = False
        for player_steamid in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_steamid]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
        self.active_player_threads_dict.clear()
        self.telnet_lines_list = None
        self.tn.tn.close()

