"""
next attempt for my bot ^^ this time a bit more organized.

takes command line options like so:
python chrani-bot.py 127.0.0.1 8081 12345678 dummy.sqlite --verbosity=DEBUG
"""
import time
import math
import re
from telnet_connection import TelnetConnection
"""
command line parser for configurations
"""
from command_line_args import args_dict
"""
Logging
"""
from logger import logger


if __name__ == '__main__':
    """
    let there be bot:
    """
    logger.info("chrani-bot started")
    logger.debug("trying to connect to (" + args_dict["Telnet-password"] + "@" + args_dict['IP-address'] + ":" + str(
        args_dict["Telnet-port"]) + ")")

    """ PlayerSpawnedInWorld reasons:
    NewGame, JoinMultiplayer, Teleport, Died, LoadedGame, EnterMultiplayer
    """
    match_types = {
        'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: \'(?P<player_name>.*)\': /(?P<command>.+)\r",
        'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)\r",
        'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), .* PlayerName='(?P<player_name>.*)'\r",
    }
    match_types_system = {
        'player_line_regexp': r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\n*",
        'telnet_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command \'(?P<telnet_command>.*)\' from client (?P<player_steamid>.+)\r",
        'telnet_player_disconnected': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes\r",
    }


    def get_region_string(pos_x, pos_z):
        grid_x = int(math.floor(pos_x / 512))
        grid_z = int(math.floor(pos_z / 512))

        return str(grid_x) + "." + str(grid_z) + ".7.rg"

    def listplayers_to_dict(listplayers):
        online_players_dict = {}
        if listplayers is None:
            listplayers = ""
        player_line_regexp = match_types_system["player_line_regexp"]
        for m in re.finditer(player_line_regexp, listplayers):
            """
            m.group(16) = steamid
            """
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
                "ping": int(m.group(18)),
                "region": get_region_string(float(m.group(3)), float(m.group(5))),
            }})
        return online_players_dict


    import collections

    def deep_update(source, overrides):
        """
        Update a nested dictionary or similar mapping.

        Modify ``source`` in place.
        """
        for key, value in overrides.iteritems():
            if isinstance(value, collections.Mapping) and value:
                returned = deep_update(source.get(key, {}), value)
                source[key] = returned
            else:
                source[key] = overrides[key]
        return source

    from threading import Event
    from player_observer import PlayerObserver
    from actions_authentication import actions_authentication
    from actions_lobby import actions_lobby, observers_lobby
    from actions_home import actions_home

    rot_old = {}
    pos_old = {}
    vitals_old = {}

    def store_player_lifesigns(player):
        rot_old.update(
            {player["name"]: {"rot_x": player["rot_x"], "rot_y": player["rot_y"], "rot_z": player["rot_z"]}})
        pos_old.update(
            {player["name"]: {"pos_x": player["pos_x"], "pos_y": player["pos_y"], "pos_z": player["pos_z"]}})

    def check_if_lifesigns_have_changed(player):
        if player["rot_x"] != rot_old[player["name"]]["rot_x"] or player["rot_y"] != rot_old[player["name"]]["rot_y"] or player["rot_z"] != rot_old[player["name"]]["rot_z"]:
            if player["is_in_limbo"]:
                logger.debug(player["name"] + ": change detected! setting player-status ALIVE (rot)")
                tn.say("bot is tracking you!")
                return True

        if player["pos_x"] != pos_old[player["name"]]["pos_x"] or player["pos_y"] != pos_old[player["name"]]["pos_y"] or player["pos_z"] != pos_old[player["name"]]["pos_z"]:
            if player["is_in_limbo"]:
                logger.debug(player["name"] + ": change detected! setting player-status ALIVE (pos)")
                tn.say("bot is tracking you!")
                return True
        return False

    while True:
        """
        outer loop to catch fatal server errors
        """
        players_dict = {}
        locations_dict = {'lobby': {'pos_x': 117, 'pos_y': 111, 'pos_z': -473, 'radius': 5}}
        active_threads = {}
        try:
            tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'],
                                  args_dict['Telnet-password'])

            tn.say("Bot is active")
            while True:
                """
                this is the main loop. do your magic here!
                """
                try:
                    listplayers_raw, count = tn.listplayers()
                    list_players_dict = listplayers_to_dict(listplayers_raw)
                    deep_update(players_dict, list_players_dict)  # deep update, since we have a nested Dict

                    for player_name, online_player in players_dict.iteritems():
                        try:
                            player_observer_thread = active_threads[player_name]["thread"]
                            if telnet_line is not None:
                                player_observer_thread.update_telnet_line(telnet_line)
                            player_observer_thread.update_player(online_player)
                            player_observer_thread.update_locations(locations_dict)
                            if check_if_lifesigns_have_changed(online_player):
                                online_player.update({"is_in_limbo": False})
                        except KeyError:
                            store_player_lifesigns(online_player)
                            online_player.update({"is_in_limbo": True})

                            stop_flag = Event()
                            player_observer_thread = PlayerObserver(stop_flag, online_player)
                            player_tn = TelnetConnection(args_dict['IP-address'], args_dict['Telnet-port'], args_dict['Telnet-password'])
                            player_observer_thread.tn = player_tn
                            player_observer_thread.match_types = match_types
                            player_observer_thread.actions = actions_authentication + actions_home + actions_lobby
                            player_observer_thread.observers = observers_lobby
                            player_observer_thread.locations = locations_dict
                            player_observer_thread.name = player_name
                            player_observer_thread.isDaemon()
                            player_observer_thread.start()

                            active_threads.update({player_name: {"event": stop_flag, "thread": player_observer_thread}})
                            logger.debug("thread started for player " + player_name)

                    telnet_line = tn.read_line(b"\r\n")
                    if telnet_line is not None:
                        """
                        do all system relevant actions here
                        these should not be touched unless you know exactly what you are doing, as every other method in
                        this bot will rely on this data
                        """
                        m = re.search(match_types["telnet_events_player"], telnet_line)
                        if m:
                            if m.group("command") == "died" or m.group("command").startswith("killed by"):
                                for player_name, online_player in players_dict.iteritems():
                                    if player_name == m.group("player_name"):
                                        store_player_lifesigns(online_player)
                                        online_player.update({"is_in_limbo": True})

                            elif m.group("command") == "joined the game":
                                for player_name, online_player in players_dict.iteritems():
                                    if player_name == m.group("player_name"):
                                        online_player.update({"is_in_limbo": False})

                        m = re.search(match_types_system["telnet_player_disconnected"], telnet_line)
                        if m:
                            if m.group("command") == "disconnected":
                                try:
                                    player_name = m.group("player_name")
                                    stop_flag = active_threads[player_name]["event"]
                                    stop_flag.set()
                                    logger.debug("thread stopped for player " + player_name + " after " + str(
                                        m.group("time")) + " minutes")
                                except KeyError:
                                    pass
                                del players_dict[player_name]
                                del active_threads[player_name]

                        m = re.search(match_types["telnet_events_playerspawn"], telnet_line)
                        if m:
                            if m.group("command") == "Died" or m.group("command") == "Teleport":
                                for player_name, online_player in players_dict.iteritems():
                                    if player_name == m.group("player_name"):
                                        online_player.update({"is_in_limbo": False})

                        m = re.search(match_types_system["telnet_commands"], telnet_line)
                        if m:
                            if m.group("telnet_command").startswith("tele "):
                                c = re.search(r"^tele (?P<player_name>.*) (?P<pos_x>.*) (?P<pos_y>.*) (?P<pos_z>.*)", m.group("telnet_command"))
                                if c:
                                    store_player_lifesigns(players_dict[c.group("player_name")])
                                    players_dict[c.group("player_name")].update({"is_in_limbo": True})

                except Exception:
                    raise

        except Exception as error:
            """
            connection lost, stop all local player_events, remove live-data
            attempt reconnection!
            """
            try:
                for player_name, online_player in active_threads.iteritems():
                    if "event" in online_player:
                        stop_flag = online_player["event"]
                        stop_flag.set()
                        # thread = online_player["thread"]
                        # thread.stopped.set()
                        logger.debug("thread stopped for player " + player_name)

                players_dict.clear()
            except NameError:
                pass

            wait_until_reconnect = 5
            logger.warn(error)
            log_message = 'will try again in ' + str(wait_until_reconnect) + " seconds"
            logger.info(log_message)
            time.sleep(wait_until_reconnect)
