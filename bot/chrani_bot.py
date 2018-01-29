from threading import Event
import time
import re
from bot.command_line_args import args_dict
from bot.telnet_connection import TelnetConnection
from bot.logger import logger
from bot.locations import Locations
from bot.whitelist import Whitelist
from bot.player import Player
from bot.players import Players
from bot.player_observer import PlayerObserver


class ChraniBot():
    name = str
    is_active = bool  # used for restarting the bot safely after connection loss

    match_types = dict
    match_types_system = dict

    tn = object  # telnet connection to use
    telnet_lines = list

    listplayers_interval = int

    active_player_threads_dict = dict  # contains link to the players observer-thread

    players = object
    locations = object
    whitelist = object

    def __init__(self):
        self.active_player_threads_dict = {}
        self.name = "chrani-bot"
        self.is_active = False  # used for restarting the bot safely after connection loss

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
            # the game logs several playerevents with additional information (for now i only capture the one i need, but there are several more useful ones
            'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), position: (?P<pos_x>.*), (?P<pos_y>.*), (?P<pos_z>.*)\): EntityID=(?P<entity_id>.*), PlayerID='(?P<steamid>.*), OwnerID='(?P<owner_steamid>.*)', PlayerName='(?P<player_name>.*)'",
            # isolates the diconnected log entry to get the total session time of a player easily
            'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",
            # to parse the telnets listplayers response
            'listplayers_result_regexp': r"\d{1,2}. id=(\d+), (.+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\r\n",
            # player joined / died messages
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)"
        }

        self.listplayers_interval = 1

        self.players = Players()
        self.locations = Locations()
        self.whitelist = Whitelist()

        self.tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])

        # players will be updated at a regular interval, no need to preload anything
        # self.players.load_all()
        self.locations.load_all()  # load all location data
        self.whitelist.load_all()  # load all whitelisted players
        self.is_active = True  # this is set so the main loop can be started / stopped

    def listplayers_to_dict(self, listplayers):
        """
        Return the list of player as a dict.
        :param listplayers: (str) players online
        :return: (list) players
        """
        online_players_dict = {}
        if listplayers is None:
            listplayers = ""
        player_line_regexp = self.match_types_system["listplayers_result_regexp"]
        for m in re.finditer(player_line_regexp, listplayers):
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

    def shutdown(self):
        self.is_active = False
        for player_steamid in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_steamid]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
        self.active_player_threads_dict.clear()
        self.telnet_line = None
        self.tn.connection.close()

    def run(self):
        logger.info("chrani-bot started")
        self.tn.say("chrani-bot started")
        self.tn.togglechatcommandhide("/")

        log_main_loop_interval = 5  # print player status ever ten seconds or so
        log_main_loop_start = 0
        log_main_loop_timeout = 0  # should log first, then timeout ^^

        listplayers_start = time.time()
        listplayers_timeout = 0  # should poll first, then timeout ^^
        bot_main_loop_execution_time = 0
        while self.is_active:
            bot_main_loop_start = time.time()

            """ update player-data at a set interval (self.listplayers_interval)
            we will load data for each player from storage, if available and
            create a new player_object if it isn't available in storage and save it (new player)
            we will keep the data in memory updated with the data polled from the telnet for all currently
            online players
            """
            if (bot_main_loop_start - listplayers_start) >= listplayers_timeout:
                listplayers_start = time.time()
                listplayers_timeout = self.listplayers_interval
                # get all currently online players and store them in a dictionary
                listplayers_raw, count = self.tn.listplayers()
                listplayers_dict = self.listplayers_to_dict(listplayers_raw)

                # prune players not online anymore
                for player in set(self.players.players_dict) - set(listplayers_dict.keys()):
                    del self.players.players_dict[player]

                # create new player entries / update existing ones
                for player_steamid, player_dict in listplayers_dict.iteritems():
                    try:
                        player_object = self.players.get(player_steamid)
                        # player is already online and needs updating
                        player_object.update(**player_dict)
                        self.players.upsert(player_object)
                    except KeyError:  # player is not currently online!
                        try:
                            player_object = self.players.load(player_steamid)
                            # player has a file on disc, update it!
                            player_object.update(**player_dict)
                            self.players.upsert(player_object)
                        except KeyError:  # player is totally new
                            player_object = Player(**player_dict)
                            self.players.upsert(player_object, save=True)
                    # there should be a valid object state here now ^^

                log_message = "executed 'listplayers' - {} players online (i do this every {} seconds, it took me {} seconds)".format(count, self.listplayers_interval, time.time() - listplayers_start)
                logger.debug(log_message)

            """ handle player-threads """
            for player_steamid, online_player in self.players.players_dict.iteritems():
                """ start player_observer_thread for each player not already being observed """
                if player_steamid not in self.active_player_threads_dict:
                    stop_flag = Event()
                    player_observer_thread = PlayerObserver(self, stop_flag, str(player_steamid))  # I'm passing the bot (self) into it to have easy access to it's variables
                    player_observer_thread.name = player_steamid  # nice to have for the logs
                    player_observer_thread.isDaemon()
                    player_observer_thread.start()

                    self.active_player_threads_dict.update({player_steamid: {"event": stop_flag, "thread": player_observer_thread}})
                    logger.debug("thread started for player " + online_player.name)

                    if online_player.is_alive() is True:
                        # if they have health, we can assume the players are alive and can be manhandled by the bot!
                        online_player.switch_on("main - initial switch-on")

            for player_steamid in set(self.active_player_threads_dict) - set(self.players.players_dict.keys()):
                """ prune all active_player_threads from players no longer online """
                active_player_thread = self.active_player_threads_dict[player_steamid]
                stop_flag = active_player_thread["thread"]
                stop_flag.stopped.set()
                del self.active_player_threads_dict[player_steamid]

            try:
                self.telnet_lines = self.tn.read_line()  # get the current global telnet-response
            except Exception as e:
                logger.error(e)
                raise IOError

            if self.telnet_lines is not None:
                for telnet_line in self.telnet_lines:
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
                                        player_object.switch_on("main - joined the game")

                    m = re.search(self.match_types_system["telnet_events_playerspawn"], telnet_line)
                    if m:
                        if m.group("command") == "Died" or m.group("command") == "Teleport":
                            for player_steamid, player_object in self.players.players_dict.iteritems():
                                if player_object.name == m.group("player_name"):
                                    try:
                                        player_object = self.players.players_dict[player_steamid]
                                        player_object.pos_x = m.group('pos_x')
                                        player_object.pos_y = m.group('pos_y')
                                        player_object.pos_z = m.group('pos_z')
                                        self.players.upsert(player_object, save=True)
                                        player_object.switch_on("main - respawned")
                                    except KeyError:
                                        pass

                    """ send telnet_line to player-thread
                    check any telnet-line for any known playername currently online
                    """
                    for player_steamid, player_object in self.players.players_dict.iteritems():
                        possible_action_for_player = re.search(player_object.name, telnet_line)
                        if possible_action_for_player:
                            if player_steamid in self.active_player_threads_dict:
                                active_player_thread = self.active_player_threads_dict[player_steamid]
                                active_player_thread["thread"].trigger_action(telnet_line)

                if time.time() - log_main_loop_start > log_main_loop_timeout:
                    log_message = "executed main bot loop. That took me about {} seconds)".format(time.time() - bot_main_loop_start)
                    logger.debug(log_message)

                    log_main_loop_start = time.time()
                    log_main_loop_timeout = (log_main_loop_interval - 1)
