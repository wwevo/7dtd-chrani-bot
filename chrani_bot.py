from threading import Event
from datetime import datetime
import re

from logger import logger
from player import Player
from player_observer import PlayerObserver

from location import Location


class ChraniBot():
    tn = None  # telnet connection to use
    is_active = None  # used for restarting the bot safely after connection loss

    match_types = {
        'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: \'(?P<player_name>.*)\': /(?P<command>.+)\r",
        'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)\r",
        'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), .* PlayerName='(?P<player_name>.*)'\r",
        'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes\r",
        'telnet_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command \'(?P<telnet_command>.*)\' from client (?P<player_steamid>.+)\r"
    }

    telnet_line = None

    listplayers_interval = 1
    online_players_dict = {}  # contains all currently online players
    active_player_threads_dict = {}

    locations_dict = {}

    def __init__(self):
        self.locations_dict.update({"lobby": {'pos_x': 117, 'pos_y': 111, 'pos_z': -473, 'radius': 5}})
        pass

    def activate(self):
        self.is_active = True

    def shutdown(self):
        self.is_active = False
        for player_name in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_name]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
        self.active_player_threads_dict.clear()
        self.online_players_dict.clear()
        self.locations_dict.clear()
        self.match_types.clear()
        self.telnet_line = None
        self.tn = None

    def setup_telnet_connection(self, telnet_connection):
        self.tn = telnet_connection

    def add_match_type(self, match_type_dict={}):
        for match_type_name, match_type_regexp in match_type_dict.iteritems():
            self.match_types.update({match_type_name: match_type_regexp})

    def listplayers_to_dict(self, listplayers):
        online_players_dict = {}
        if listplayers is None:
            listplayers = ""
        player_line_regexp = self.match_types["listplayers_result_regexp"]
        for m in re.finditer(player_line_regexp, listplayers):
            online_players_dict.update({m.group(2): {
                "id": m.group(1),
                "name": str(m.group(2)),
                "pos_x": float(m.group(3)),
                "pos_y": float(m.group(4)),
                "pos_z": float(m.group(5)),
                "rot_x": float(m.group(6)),
                "rot_y": float(m.group(7)),
                "rot_z": float(m.group(8)),
                "remote": bool(m.group(9)),
                "health": int(m.group(10)),
                "deaths": int(m.group(11)),
                "zombies": int(m.group(12)),
                "players": int(m.group(13)),
                "score": m.group(14),
                "level": m.group(15),
                "steamid": m.group(16),
                "ip": str(m.group(17)),
                "ping": int(m.group(18))
            }})
        return online_players_dict

    def prune_active_player_threads_dict(self):
        for player_name in set(self.active_player_threads_dict) - set(self.online_players_dict.keys()):
            """ prune all active_player_threads from players no longer online """
            active_player_thread = self.active_player_threads_dict[player_name]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
            del self.active_player_threads_dict[player_name]

    def run(self):
        logger.info("chrani-bot started")

        listplayers_start = datetime.now()
        listplayers_timeout = 0  # should poll first, then timeout ^^
        while self.is_active:

            """ manage currently online players dict """
            if (datetime.now() - listplayers_start).total_seconds() > listplayers_timeout:
                """ get all currently online players and store them in a dictionary """
                listplayers_start = datetime.now()
                listplayers_raw, count = self.tn.listplayers()
                log_message = "executed 'listplayers' - " + count + " players online (I do this every " + str(self.listplayers_interval) + " seconds)"
                logger.debug(log_message)
                listplayers_dict = self.listplayers_to_dict(listplayers_raw)

                """ create new player entries / update existing ones """
                for player_name, player_dict in listplayers_dict.iteritems():
                    if player_name in self.online_players_dict:
                        self.online_players_dict[player_name].update(**player_dict)
                    else:
                        self.online_players_dict.update({player_name: Player(**player_dict)})

                """ prune players not online anymore """
                for player in set(self.online_players_dict) - set(listplayers_dict.keys()):
                    del self.online_players_dict[player]

                listplayers_timeout = self.listplayers_interval

            self.telnet_line = self.tn.read_line(timeout=self.listplayers_interval)  # get the current global telnet-response
            if self.telnet_line is not None:
                logger.debug(self.telnet_line)

            """ handle player-threads """
            for player_name, online_player in self.online_players_dict.iteritems():
                """ start player_observer_thread for each player not already being observed """
                if player_name not in self.active_player_threads_dict:
                    stop_flag = Event()
                    player_observer_thread = PlayerObserver(self, stop_flag, online_player)  # I'm passing the bot (self) into it to have easy access to it's variables
                    player_observer_thread.name = player_name  # nice to have for the logs
                    player_observer_thread.isDaemon()
                    player_observer_thread.start()

                    self.active_player_threads_dict.update({player_name: {"event": stop_flag, "thread": player_observer_thread}})
                    logger.debug("thread started for player " + player_name)

            self.prune_active_player_threads_dict()

            """ handle player-death-and-respawn-events, 'suspending' threads if needed! """
            if self.telnet_line is not None:
                m = re.search(self.match_types["telnet_events_player"], self.telnet_line)
                if m:
                    if m.group("command") == "died" or m.group("command").startswith("killed by"):
                        for player_name, online_player in self.online_players_dict.iteritems():
                            if player_name == m.group("player_name"):
                                if player_name in self.active_player_threads_dict:
                                    active_player_thread = self.active_player_threads_dict[player_name]
                                    active_player_thread["thread"].player_is_alive = False
                                    logger.debug("switched off player")

                m = re.search(self.match_types["telnet_events_playerspawn"], self.telnet_line)
                if m:
                    if m.group("command") == "Died" or m.group("command") == "Teleport":
                        for player_name, online_player in self.online_players_dict.iteritems():
                            if player_name == m.group("player_name"):
                                if player_name in self.active_player_threads_dict:
                                    active_player_thread = self.active_player_threads_dict[player_name]
                                    active_player_thread["thread"].player_is_alive = True
                                    logger.debug("switched on player")

                m = re.search(self.match_types["telnet_commands"], self.telnet_line)
                if m:
                    if m.group("telnet_command").startswith("tele "):
                        c = re.search(r"^tele (?P<player_name>.*) (?P<pos_x>.*) (?P<pos_y>.*) (?P<pos_z>.*)", m.group("telnet_command"))
                        if c:
                            active_player_thread = self.active_player_threads_dict[c.group('player_name')]
                            active_player_thread["thread"].player_is_alive = False
                            logger.debug("switched off player")

            """ trigger chat actions for players """
            if self.telnet_line is not None:
                for player_name, player_dict in self.online_players_dict.iteritems():
                    possible_action_for_player = re.search(player_name, self.telnet_line)
                    if possible_action_for_player:
                        if player_name in self.active_player_threads_dict:
                            active_player_thread = self.active_player_threads_dict[player_name]
                            active_player_thread["thread"].trigger_chat_action(self.telnet_line)
