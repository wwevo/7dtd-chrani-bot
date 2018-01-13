from threading import Event
import time
import re
from logger import logger
from player import Player
from player_observer import PlayerObserver

from location import Location


class ChraniBot():
    name = "chrani-bot"
    is_active = None  # used for restarting the bot safely after connection loss

    match_types = {
        # matches any command a player issues in game-chat
        'chat_commands':                r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: \'(?P<player_name>.*)\': /(?P<command>.+)\r",
        # player joined / died messages etc
        'telnet_events_player':         r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*): (?P<steamid>\d+)\r",
        'telnet_events_player_gmsg':    r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)\r"
    }

    match_types_system = {
        # captures the response for telnet commands. used for example to capture teleport response
        'telnet_commands':              r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command \'(?P<telnet_command>.*)\' from client (?P<player_steamid>.+)\r",
        # the game logs several playerevents with additional information (for now i only capture the one i need, but there are several more useful ones
        'telnet_events_playerspawn':    r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), .* PlayerName='(?P<player_name>.*)'\r",
        # isolates the diconnected log entry to get the total session time of a player easily
        'telnet_player_disconnected':   r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes\r",
        # to parse the telnets listplayers response
        'listplayers_result_regexp':    r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\r\n",
        # player joined / died messages
        'telnet_events_player_gmsg':    r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)\r"
    }

    tn = None  # telnet connection to use
    telnet_line = None

    listplayers_interval = 1.25

    players_dict = {}  # contains all player_objects of online players
    active_player_threads_dict = {}  # contains link to the players observer-thread

    locations_dict = {}  # contains all location objects

    def __init__(self):
        pass

    def activate(self):
        self.is_active = True

    def setup_telnet_connection(self, telnet_connection):
        self.tn = telnet_connection

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
            online_players_dict.update({m.group(2): {
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

    def prune_active_player_threads_dict(self):
        for player_name in set(self.active_player_threads_dict) - set(self.players_dict.keys()):
            """ prune all active_player_threads from players no longer online """
            active_player_thread = self.active_player_threads_dict[player_name]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
            del self.active_player_threads_dict[player_name]

    def shutdown(self):
        self.is_active = False
        for player_name in self.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.active_player_threads_dict[player_name]
            stop_flag = active_player_thread["thread"]
            stop_flag.stopped.set()
        self.active_player_threads_dict.clear()
        #  self.players_dict.clear()

        self.telnet_line = None
        self.tn.connection.close()

    def run(self):
        """
        Start the loop of the bot consuming events.
        :return:
        """
        logger.info("chrani-bot started")
        self.tn.say("chrani-bot started")
        self.tn.togglechatcommandhide("/")

        listplayers_start = time.time()
        listplayers_timeout = 0  # should poll first, then timeout ^^
        bot_main_loop_execution_time = 0
        while self.is_active:
            bot_main_loop_start = time.time()
            # player online part
            if (time.time() - listplayers_start) > listplayers_timeout:
                """ manage currently online players dict

                do this at a set interval, the listplayers_interval in fact as this only make sense with fresh data
                """
                # get all currently online players and store them in a dictionary
                listplayers_start = time.time()
                listplayers_raw, count = self.tn.listplayers()

                listplayers_dict = self.listplayers_to_dict(listplayers_raw)

                # create new player entries / update existing ones
                for player_name, player_dict in listplayers_dict.iteritems():
                    if player_name in self.players_dict:
                        self.players_dict[player_name].update(**player_dict)
                    else:
                        self.players_dict[player_name] = Player(**player_dict)

                # prune players not online anymore """
                for player in set(self.players_dict) - set(listplayers_dict.keys()):
                    del self.players_dict[player]

                log_message = "executed 'listplayers' - {} players online (i do this every {} seconds, it took me {} seconds)".format(count, self.listplayers_interval, time.time() - listplayers_start)
                # logger.debug(log_message)

            # TODO telnet_line could be a local variable instead of an attribute as it's not use in another method, not sure to be confirmed
            self.telnet_line = self.tn.read_line(timeout=listplayers_timeout)  # get the current global telnet-response
            if self.telnet_line is not None and self.telnet_line != b"\r\n":
                telnet_line_stripped = self.telnet_line.rstrip()
                logger.info(telnet_line_stripped)

            if self.players_dict:  # only need to run the functions if a player is online
                """ handle player-threads """
                for player_name, online_player in self.players_dict.iteritems():
                    """ start player_observer_thread for each player not already being observed """
                    if player_name not in self.active_player_threads_dict:
                        stop_flag = Event()
                        player_observer_thread = PlayerObserver(self, stop_flag,
                                                                online_player)  # I'm passing the bot (self) into it to have easy access to it's variables
                        player_observer_thread.name = player_name  # nice to have for the logs
                        player_observer_thread.isDaemon()
                        player_observer_thread.start()

                        self.active_player_threads_dict.update(
                            {player_name: {"event": stop_flag, "thread": player_observer_thread}})
                        logger.debug("thread started for player " + player_name)

            self.prune_active_player_threads_dict()

            if self.telnet_line is not None:
                """ manage system relevant events
                
                we have an active telnet line and a list of players available
                we now need to mak sure the player is in a state able to receive commands or messages or whatever in
                order to allow enhanced functions like teleports, which can bug the game out if used at the wrong times
                
                teleports for example may never be used on a dead player, or one currently in the
                bedroll-screen as that will effectively shut the player out, presenting a black screen requiring
                relogging and then causing the player to die again... fun times
                
                there's an additional lifesign-check in the player_observer for each player, this one is still needed as
                the telnet-repsonse is way more 'instant'. the lifesign-check is dependent on the player_observer
                interval
                
                here we check any telnet response relevant for setting the 'responsive' status of a player
                """
                """ check if a player is being teleported
                
                and discontinue all further execution at the earliest point
                """
                m = re.search(self.match_types_system["telnet_commands"], self.telnet_line)
                if m:
                    if m.group("telnet_command").startswith("tele "):
                        c = re.search(r"^tele (?P<player_name>.*) (?P<pos_x>.*) (?P<pos_y>.*) (?P<pos_z>.*)", m.group("telnet_command"))
                        if c:
                            try:
                                player_object = self.players_dict[c.group('player_name')]
                                player_object.switch_off("main")
                            except KeyError:
                                pass

                m = re.search(self.match_types_system["telnet_events_player_gmsg"], self.telnet_line)
                if m:
                    if m.group("command") == "died":
                        for player_name, player_object in self.players_dict.iteritems():
                            if player_name == m.group("player_name"):
                                if player_name in self.active_player_threads_dict:
                                    player_object.switch_off("main")

                    if m.group("command") == "joined the game":
                        for player_name, player_object in self.players_dict.iteritems():
                            if player_name == m.group("player_name"):
                                if player_name in self.active_player_threads_dict:
                                    player_object.switch_on("main")

                m = re.search(self.match_types_system["telnet_events_playerspawn"], self.telnet_line)
                if m:
                    if m.group("command") == "Died" or m.group("command") == "Teleport":
                        for player_name, online_player in self.players_dict.iteritems():
                            if player_name == m.group("player_name"):
                                try:
                                    player_object = self.players_dict[player_name]
                                    player_object.switch_on("main")
                                except KeyError:
                                    pass

                for player_name, player_object in self.players_dict.iteritems():
                    possible_action_for_player = re.search(player_object.name, self.telnet_line)
                    if possible_action_for_player:
                        if player_name in self.active_player_threads_dict:
                            active_player_thread = self.active_player_threads_dict[player_name]
                            active_player_thread["thread"].trigger_action(self.telnet_line)

            bot_main_loop_execution_time = time.time() - bot_main_loop_start
            listplayers_timeout = self.listplayers_interval - bot_main_loop_execution_time  # need to add modifier for execution time to get a precise interval
            log_message = "executed main bot loop. That took me about {} seconds)".format(time.time() - bot_main_loop_start)
            logger.debug(log_message)



