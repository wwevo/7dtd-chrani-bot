import re
import traceback
from time import time, sleep
from threading import *
from collections import deque
import actions

from bot.modules.logger import logger


class TelnetObserver(Thread):
    tn = object
    chrani_bot = object
    actions = object
    stopped = object

    run_observer_interval = int  # loop this every run_observers_interval seconds
    last_execution_time = float

    recent_telnet_response = str
    recent_telnet_response_has_valid_start = bool
    recent_telnet_response_has_valid_end = bool

    telnet_buffer = str
    valid_telnet_lines = deque
    action_queue = deque

    def __init__(self, event, chrani_bot, tn):
        self.tn = tn
        self.chrani_bot = chrani_bot
        self.actions = actions

        self.run_observer_interval = 0.5

        self.recent_telnet_response = None
        self.recent_telnet_response_has_valid_start = False
        self.recent_telnet_response_has_valid_end = False

        self.valid_telnet_lines = deque()
        self.telnet_buffer = ""

        self.last_execution_time = 0.0

        self.stopped = event
        Thread.__init__(self)

    def is_a_valid_line(self, telnet_line):
        telnet_response_is_a_valid_line = False
        if self.has_valid_start(telnet_line) and self.has_valid_end(telnet_line):
            telnet_response_is_a_valid_line = True

        return telnet_response_is_a_valid_line

    def has_valid_start(self, telnet_response):
        telnet_response_has_valid_start = False
        for match_type in self.chrani_bot.match_types_generic["log_start"]:
            if re.match(match_type, telnet_response):
                telnet_response_has_valid_start = True

        return telnet_response_has_valid_start

    def has_valid_end(self, telnet_response):
        telnet_response_has_valid_end = False
        for match_type in self.chrani_bot.match_types_generic["log_end"]:
            if re.search(match_type, telnet_response):
                telnet_response_has_valid_end = True

        return telnet_response_has_valid_end

    def has_mutliple_lines(self, telnet_response):
        telnet_response_has_multiple_lines = False
        telnet_response_count = telnet_response.count(b"\r\n")
        if telnet_response_count >= 1:
            telnet_response_has_multiple_lines = telnet_response_count

        return telnet_response_has_multiple_lines

    def get_lines(self, telnet_response):
        telnet_lines_list = [telnet_line for telnet_line in telnet_response.splitlines(True)]
        return telnet_lines_list

    def get_a_bunch_of_lines(self, this_many_lines):
        telnet_lines = []
        current_queue_length = 0
        done = False
        while (current_queue_length < this_many_lines) and not done:
            try:
                telnet_lines.append(self.valid_telnet_lines.popleft())
                current_queue_length += 1
            except IndexError:
                done = True

        if len(telnet_lines) >= 1:
            return telnet_lines
        else:
            return False

    def update_valid_telnet_lines(self):
        try:
            telnet_response = self.tn.read_very_eager()
        except:
            self.stopped.set()
            return False

        if len(telnet_response) > 0:
            self.telnet_buffer += telnet_response
            self.telnet_buffer = self.telnet_buffer[-4000:]

            processing_done = False
            """ telnet returned data. let's get some information about it"""
            response_count = 1
            telnet_response_components = self.get_lines(telnet_response)
            for component in telnet_response_components:
                if self.is_a_valid_line(component):
                    self.valid_telnet_lines.append(component.rstrip(b"\r\n"))
                    # logger.debug("{error_message}/{telnet_line}".format(error_message="added complete line: ", telnet_line=component.rstrip(b"\r\n")))
                else:
                    if response_count == 1:
                        # not a complete line, but the first in the list: might be the rest of last run
                        if self.recent_telnet_response is not None:
                            combined_line = "{}{}".format(self.recent_telnet_response, component)
                            if self.is_a_valid_line(combined_line):
                                self.valid_telnet_lines.append(combined_line.rstrip(b"\r\n"))
                                # logger.debug("{error_message}/{telnet_line}".format(error_message="added complete combined line: ", telnet_line=combined_line.rstrip(b"\r\n")))
                            else:
                                # logger.debug("{error_message}/{telnet_line}".format(error_message="combined line, it doesnt make sense though: ", telnet_line=combined_line.rstrip(b"\r\n")))
                                pass

                            self.recent_telnet_response = None
                        else:
                            if len(telnet_response_components) == 1:
                                if self.has_valid_start(component):
                                    # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line, storing for next run: ", telnet_line=component.rstrip(b"\r\n")))
                                    self.recent_telnet_response = component
                                else:
                                    # logger.debug("{error_message}/{telnet_line}".format(error_message="what happened?: ", telnet_line=component.rstrip(b"\r\n")))
                                    pass

                    elif response_count == len(telnet_response_components):
                        # not a complete line, but the last in the list: might be the beginning of next run
                        if self.has_valid_start(component):
                            self.recent_telnet_response = component
                            # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line, storing for next run: ", telnet_line=component.rstrip(b"\r\n")))
                        else:
                            # logger.debug("{error_message}/{telnet_line}".format(error_message="does not seem to be usable: ", telnet_line=component.rstrip(b"\r\n")))
                            pass

                    else:
                        # not a complete line right in the middle. We don't need this!!
                        # logger.debug("{error_message}/{telnet_line}".format(error_message="found incomplete line smack in the middle: ", telnet_line=component.rstrip(b"\r\n")))
                        pass

                response_count += 1

    def execute_queue(self, count):
        telnet_lines = self.get_a_bunch_of_lines(count)
        if not telnet_lines:
            return True

        for telnet_line in telnet_lines:
            m = re.search(r"(?P<datetime>.+?) (?P<stardate>.+?) INF Executing command\s'(?P<telnet_command>.*)'\s(?P<source>by Telnet|from client)\s(?(source)from(?P<ip>.*):(?P<port>.*)|(?P<player_steamid>.*))", telnet_line)
            if not m or m and m.group('telnet_command').split(None, 1)[0] not in ['mem', 'gt', 'lp', 'llp', 'llp2', 'lpf']:
                if telnet_line != '':
                    logger.debug(telnet_line)

            # # isolates the disconnected log entry to get the total session time of a player easily
            # 'telnet_player_playtime': r"(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",

            # handle playerspawns
            m = re.search(r"(?P<datetime>.+?) (?P<stardate>.+?) INF \[Steamworks.NET\]\s(?P<command>.*)\splayer:\s(?P<player_name>.*)\sSteamId:\s(?P<player_steamid>\d+)\s(.*)", telnet_line)
            if m:
                try:
                    connecting_player = self.chrani_bot.players.player_entered_telnet(m)
                    connecting_player["thread"].trigger_action(connecting_player["player_object"], "entered the stream")
                except KeyError:
                    pass

            m = re.search(r"(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*), entityid=(?P<entity_id>.*), name=(?P<player_name>.*), steamid=(?P<player_steamid>.*), steamOwner=(?P<owner_id>.*), ip=(?P<player_ip>.*)", telnet_line)
            if m:
                try:
                    connecting_player = self.chrani_bot.players.player_entered_telnet(m)
                    connecting_player["thread"].trigger_action(connecting_player["player_object"], "entered the stream")
                except KeyError:
                    pass

            # the game logs several player-events with additional information (for now i only capture the one i need, but there are several more useful ones
            m = re.search(r"(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), position: (?P<pos_x>.*), (?P<pos_y>.*), (?P<pos_z>.*)\): EntityID=(?P<entity_id>.*), PlayerID='(?P<player_steamid>.*)', OwnerID='(?P<owner_steamid>.*)', PlayerName='(?P<player_name>.*)'", telnet_line)
            if m:
                try:
                    spawning_player = self.chrani_bot.players.player_entered_the_world(m)
                    spawning_player["thread"].trigger_action(spawning_player["player_object"], "entered the world")
                except KeyError:
                    pass

            # handle other spawns
            m = re.search(r"(?P<datetime>.+?) (?P<stardate>.+?) INF (?P<command>.+?) \[type=(.*), name=(?P<zombie_name>.+?), id=(?P<entity_id>.*)\] at \((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\) Day=(\d.*) TotalInWave=(\d.*) CurrentWave=(\d.*)", telnet_line)
            if m:
                try:
                    entity_id = m.group("entity_id")
                    pos_x = m.group("pos_x")
                    pos_y = m.group("pos_y")
                    pos_z = m.group("pos_z")
                    command = m.group("command")
                    zombie_name = m.group("zombie_name")
                    player_object = self.chrani_bot.players.get_by_steamid('system')
                    if command == "Spawned" and zombie_name == "zombieScreamer":
                        villages = self.chrani_bot.locations.find_by_type('village')
                        for village in villages:
                            if village.position_is_inside_boundary((pos_x, pos_y, pos_z)):
                                self.chrani_bot.player_observer.actions.common.trigger_action(self, player_object, player_object, "remove entity {}".format(entity_id))
                except KeyError:
                    pass

            m = re.search(r"(?P<datetime>.+?)\s(?P<stardate>.+?)\sINF\sAIAirDrop:\sSpawned\ssupply\scrate\s@\s\(\((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\)\)", telnet_line)
            if m:
                try:
                    pos_x = m.group("pos_x")
                    pos_y = m.group("pos_y")
                    pos_z = m.group("pos_z")
                    player_object = self.chrani_bot.players.get_by_steamid('system')
                    self.chrani_bot.player_observer.actions.common.trigger_action(self, player_object, player_object, "an airdrop has arrived @ ({pos_x} {pos_y} {pos_z})".format( pos_x=pos_x, pos_y=pos_y, pos_z=pos_z))
                except KeyError:
                    pass

            """ send telnet_line to player-thread
            check 'chat' telnet-line(s) for any known playername currently online
            """
            for player_steamid, player_object in self.chrani_bot.players.players_dict.iteritems():
                if player_steamid in self.chrani_bot.player_observer.active_player_threads_dict and player_object.name not in self.chrani_bot.settings.get_setting_by_name(name="restricted_names"):
                    m = re.search(self.chrani_bot.match_types['chat_commands'], telnet_line)
                    if m:
                        player_name = m.group('player_name')
                        if player_name == player_object.name:
                            self.chrani_bot.player_observer.trigger_action_by_telnet(telnet_line)

        return len(telnet_lines)

    def run(self):
        logger.info("telnet observer thread started")
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            self.chrani_bot.custodian.check_in('telnet_observer', True)

            if not self.chrani_bot.has_connection:
                raise IOError("{source}/{error_message}".format(source="telnet observer", error_message="lost telnet connection :("))

            if self.chrani_bot.is_paused is not False:
                sleep(1)
                continue

            profile_start = time()

            self.update_valid_telnet_lines()

            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time

        logger.debug("telnet observer thread has stopped")
