import re
import time
from threading import Event

from bot.actions_authentication import actions_authentication
from bot.actions_dev import actions_dev
from bot.actions_home import actions_home
from bot.actions_lobby import actions_lobby, observers_lobby
from bot.actions_locations import actions_locations, observers_locations
from bot.actions_whitelist import actions_whitelist, observers_whitelist
from bot.command_line_args import args_dict
from bot.locations import Locations
from bot.logger import logger
from bot.permissions import Permissions
from bot.player import Player
from bot.player_observer import PlayerObserver
from bot.players import Players
from bot.telnet_connection import TelnetConnection
from bot.whitelist import Whitelist
from timeout import timeout_occurred


class ChraniBot:
    name = str
    is_active = bool  # used for restarting the bot safely after connection loss

    match_types = dict
    match_types_system = dict
    banned_countries_list = list

    tn = object  # telnet connection to use for everything except player-actions and player-poll
    poll_tn = object
    telnet_lines_list = list

    listplayers_interval = int

    active_player_threads_dict = dict  # contains link to the players observer-thread

    players = object
    locations = object
    whitelist = object
    permission = object

    observers = list
    player_actions = list

    def __init__(self):
        self.name = "chrani-bot"
        logger.info("{} started".format(self.name))
        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'], show_log_init=True)
        self.poll_tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])

        self.players = Players()  # players will be loaded on a need-to-load basis
        self.listplayers_interval = 1.5
        self.active_player_threads_dict = {}

        self.locations = Locations()
        self.locations.load_all()  # load all location data

        self.whitelist = Whitelist()
        self.whitelist.load_all()  # load all whitelisted players

        self.player_actions = actions_whitelist + actions_authentication + actions_locations + actions_home + actions_lobby + actions_dev
        self.observers = observers_whitelist + observers_lobby + observers_locations

        self.permission_levels_list = ['admin', 'mod', 'donator', 'regular', 'all']
        self.permissions = Permissions(self.player_actions, self.permission_levels_list)

        self.match_types = {
            # matches any command a player issues in game-chat
            'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: '(?P<player_name>.*)': /(?P<command>.+)",
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
            'listplayers_result_regexp': r"\d{1,2}. id=(\d+), (.+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\r\n",
            # player joined / died messages
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)"
        }

        self.banned_countries_list = ['CN', 'CHN', 'KP', 'PRK', 'RU', 'RUS', 'NG', 'NGA']

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

    def run(self):
        self.is_active = True  # this is set so the main loop can be started / stopped
        self.tn.togglechatcommandhide("/")

        listplayers_dict = {}
        list_players_timeout_start = 0
        while self.is_active:
            if timeout_occurred(self.listplayers_interval, list_players_timeout_start):
                # get all currently online players and store them in a dictionary
                last_listplayers_dict = listplayers_dict
                listplayers_dict = self.poll_players()
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
                        stop_flag = Event()
                        player_observer_thread = PlayerObserver(self, stop_flag, str(player_steamid))  # I'm passing the bot (self) into it to have easy access to it's variables
                        player_observer_thread.name = player_steamid  # nice to have for the logs
                        player_observer_thread.isDaemon()
                        player_observer_thread.start()
                        self.players.upsert(player_object, save=True)
                        self.active_player_threads_dict.update({player_steamid: {"event": stop_flag, "thread": player_observer_thread}})

                for player_steamid in set(self.active_player_threads_dict) - set(self.players.players_dict.keys()):
                    """ prune all active_player_threads from players no longer online """
                    active_player_thread = self.active_player_threads_dict[player_steamid]
                    stop_flag = active_player_thread["thread"]
                    stop_flag.stopped.set()
                    del self.active_player_threads_dict[player_steamid]

            try:
                self.telnet_lines_list = self.tn.read_line()  # get the current global telnet-response
            except Exception as e:
                logger.error(e)
                raise IOError

            if self.telnet_lines_list is not None:
                for telnet_line in self.telnet_lines_list:
                    m = re.search(self.match_types_system["telnet_commands"], telnet_line)
                    if m:
                        if m.group("telnet_command").startswith("tele"):
                            c = re.search(r"^(tele|teleportplayer) (?P<player>.*) (?P<pos_x>.*) (?P<pos_y>.*) (?P<pos_z>.*)", m.group("telnet_command"))
                            if c:
                                for player_steamid, player_object in self.players.players_dict.iteritems():
                                    if c.group("player") in [player_object.name, player_object.steamid]:
                                        player_object.switch_off("main - teleportplayer")

                    m = re.search(self.match_types_system["telnet_events_player_gmsg"], telnet_line)
                    if m:
                        if m.group("command") == "died":
                            for player_steamid, player_object in self.players.players_dict.iteritems():
                                if player_object.name == m.group("player_name"):
                                    if player_steamid in self.active_player_threads_dict:
                                        player_object.switch_off("main - died")

                        if m.group("command") == "joined the game":
                            for player_steamid, player_object in self.players.players_dict.iteritems():
                                if player_object.name == m.group("player_name"):
                                    if player_steamid in self.active_player_threads_dict:
                                        if player_object.has_health() is True:
                                            player_object.switch_on("main - joined the game")

                    m = re.search(self.match_types_system["telnet_events_playerspawn"], telnet_line)
                    if m:
                        if m.group("command") == "Died" or m.group("command") == "Teleport":
                            for player_steamid, player_object in self.players.players_dict.iteritems():
                                if player_object.name == m.group("player_name"):
                                    try:
                                        player_object.switch_on("main - respawned")
                                    except KeyError:
                                        pass

                    """ send telnet_line to player-thread
                    check any telnet-line for any known playername currently online
                    """
                    for player_steamid, player_object in self.players.players_dict.iteritems():
                        possible_action_for_player = re.search(player_object.name, telnet_line)
                        if possible_action_for_player:
                            logger.info(telnet_line)
                            if player_steamid in self.active_player_threads_dict and player_object.is_responsive is True:
                                active_player_thread = self.active_player_threads_dict[player_steamid]
                                active_player_thread["thread"].trigger_action(telnet_line)

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

