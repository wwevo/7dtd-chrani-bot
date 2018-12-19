import traceback
from threading import *
import time
import math
import os

from collections import deque
from threading import Event

from bot.assorted_functions import multiple, timeout_occurred
from bot.modules.settings import Settings

from bot.modules.custodian import Custodian
from bot.modules.telnet_observer import TelnetObserver
from bot.modules.player_observer import PlayerObserver
from bot.modules.logger import logger

import bot.modules.global_observer as global_observer
import bot.modules.global_scheduler as global_scheduler
from bot.modules.global_scheduler import run_schedulers

from bot.objects.player import Player
from bot.objects.telnet import Telnet
from bot.modules.locations import Locations
from bot.modules.permissions import Permissions
from bot.modules.players import Players
from bot.modules.whitelist import Whitelist


class ChraniBot(Thread):
    dom = dict
    bot_version = str

    app = object
    flask = object
    flask_login = object
    socketio = object
    reboot_thread = object

    time_launched = float
    time_running = float
    server_time_running = float
    oberservers_execution_time = float
    uptime = str
    restart_in = int
    current_gametime = dict
    ready_for_action = bool
    is_active = bool  # used for restarting the bot safely after connection loss
    is_paused = bool  # used to pause all processing without shutting down the bot
    has_connection = bool
    initiate_shutdown = bool

    match_types = dict
    match_types_generic = dict

    telnet_lines_list = deque

    first_run = bool
    last_execution_time = float
    restart_delay = int
    reboot_imminent = bool
    telnet_queue = int

    chat_colors = dict
    passwords = dict
    banned_countries_list = list

    settings_dict = dict
    server_settings_dict = dict

    landclaims_dict = dict

    players = object
    locations = object
    whitelist = object
    webinterface = object
    permission = object
    settings = object
    telnet_observer = object
    player_observer = object
    custodian = object

    observers_dict = dict
    observers_controller = dict
    actions_list = list
    schedulers_dict = dict
    schedulers_controller = dict

    def __init__(self, event, app, flask, flask_login, socketio):
        self.app = app
        self.flask = flask
        self.flask_login = flask_login
        self.socketio = socketio

        self.settings = Settings()
        self.dom = {
            "bot_name": self.settings.get_setting_by_name(name='bot_name'),
            "bot_version": "0.7.354"
        }

        self.reboot_thread = None
        self.is_paused = False
        self.has_connection = False
        self.time_launched = time.time()
        self.current_gametime = None
        self.time_running = None
        self.reboot_imminent = False
        self.restart_in = 0
        self.server_time_running = None
        self.uptime = "not available"
        self.initiate_shutdown = False
        self.oberservers_execution_time = 0.0
        self.restart_delay = 0
        self.first_run = True
        self.last_execution_time = 0.0
        self.telnet_queue = 0
        self.ready_for_action = False
        self.server_settings_dict = {}

        logger.info("{} started".format(self.dom['bot_name']))

        self.players = Players()  # players will be loaded on a need-to-load basis

        self.observers_dict = global_observer.observers_dict
        self.observers_controller = global_observer.observers_controller

        self.schedulers_dict = global_scheduler.schedulers_dict
        self.schedulers_controller = global_scheduler.schedulers_controller

        self.landclaims_dict = {}

        self.whitelist = Whitelist()
        if self.settings.get_setting_by_name(name='whitelist_active') is not False:
            self.whitelist.activate()

        self.locations = Locations()

        self.passwords = self.settings.get_setting_by_name(name='authentication_groups')

        self.permission_levels_list = self.passwords.keys()  # ['admin', 'mod', 'donator', 'authenticated']

        self.chat_colors = self.settings.get_setting_by_name(name='chatbox_color_scheme', default={
            "standard": "afb0b2",
            "highlight": "b3b8bc",
            "header": "e57255",
            "warning": "e5c453",
            "success": "52d273",
            "error": "e95065",
            "info": "46bddf"
        })

        self.match_types = {
            # matches any command a player issues in game-chat
            'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF (.*) handled by mod (.+?): Chat(.*): '(?P<player_name>.*)': /(?P<command>.*)$",
            # player joined / died messages etc
            'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*): (?P<steamid>\d+)",
            'telnet_events_player_gmsg': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)",
            'hacker_stacksize': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Player\swith\sID\s(?P<entity_id>[0-9]+)\s(?P<command>.*)"
        }

        self.match_types_generic = {
            'log_start': [
                r"\A(?P<datetime>\d{4}.+?)\s(?P<time_in_seconds>.+?)\sINF .*",
                r"\ATime:\s(?P<time_in_minutes>.*)m\s",
            ],
            'log_end': [
                r"\r\n$",
                r"\sby\sTelnet\sfrom\s(.*)\:(\d.*)\s*$"
            ]
        }

        self.banned_countries_list = self.settings.get_setting_by_name(name='banned_countries')
        self.stopped = event
        Thread.__init__(self)

    def load_from_db(self):
        self.settings.load_all()
        self.players.load_all()
        self.locations.load_all()  # load all location data to memory
        self.whitelist.load_all()  # load all whitelisted players
        self.permissions.load_all()  # get the permissions or create new permissions-file

    def manage_landclaims(self):
        polled_lcb = self.telnet_observer.actions.get_active_action_result('system', "llp")
        if polled_lcb != self.landclaims_dict:
            self.landclaims_dict = polled_lcb
            lcb_owners_to_delete = {}
            lcb_owners_to_update = {}
            lcb_owners_to_update.update(self.landclaims_dict)
            for lcb_widget_owner in lcb_owners_to_update.keys():
                try:
                    player_object = self.players.get_by_steamid(lcb_widget_owner)
                except KeyError:
                    continue

                self.socketio.emit('refresh_player_lcb_widget', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')

            self.socketio.emit('update_leaflet_markers', self.get_lcb_marker_json(lcb_owners_to_update), namespace='/chrani-bot/public')
            self.socketio.emit('remove_leaflet_markers', self.get_lcb_marker_json(lcb_owners_to_delete), namespace='/chrani-bot/public')

    def get_lcb_marker_json(self, lcb_dict):
        lcb_list_final = []
        try:
            land_claim_size = int(self.server_settings_dict["LandClaimSize"])
        except TypeError:
            return lcb_list_final

        for lcb_owner_steamid, lcb_list in lcb_dict.iteritems():
            try:
                player_object = self.players.get_by_steamid(lcb_owner_steamid)
            except KeyError:
                player_dict = {
                        "name": "unknown player",
                        "steamid": lcb_owner_steamid,
                    }
                player_object = Player(**player_dict)

            for lcb in lcb_list:
                lcb_list_final.append({
                    "id": "{}_lcb_{}{}{}".format(str(player_object.steamid), str(lcb[0]), str(lcb[1]), str(lcb[2])),
                    "owner": str(player_object.steamid),
                    "identifier": "{}_lcb_{}{}{}".format(str(player_object.steamid), str(lcb[0]), str(lcb[1]), str(lcb[2])),
                    "name": str(player_object.name),
                    "radius": int((land_claim_size - 1) / 2),
                    "inner_radius": 3,
                    "pos_x": int(lcb[0]),
                    "pos_y": int(lcb[1]),
                    "pos_z": int(lcb[2]),
                    "shape": "square",
                    "type": "standard marker",
                    "layerGroup": "landclaims"
                })

        return lcb_list_final

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
        distance = math.floor(int(self.server_settings_dict['LandClaimSize']) / 2) + int(self.server_settings_dict['LandClaimDeadZone'])  # (landclaim size / 2) + Deadzone
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

    def is_it_horde_day(self, current_day):
        horde_day = False
        if multiple(current_day, 7):
            horde_day = True

        return horde_day

    def ongoing_bloodmoon(self):
        if self.current_gametime is None:
            return False

        bloodmoon = False
        if self.is_it_horde_day(int(self.current_gametime["day"])) and int(self.current_gametime["hour"]) >= 21:
            bloodmoon = True

        day_after_bloodmoon = False
        if self.is_it_horde_day(int(self.current_gametime["day"]) - 1) and int(self.current_gametime["hour"]) < 4:
            day_after_bloodmoon = True

        if bloodmoon or day_after_bloodmoon:
            return True

        return False

    def start_custodian(self):
        custodian_thread_stop_flag = Event()
        custodian_thread = Custodian(custodian_thread_stop_flag, self)
        custodian_thread.name = "custodian"
        custodian_thread.isDaemon()
        self.custodian = custodian_thread
        self.custodian.start()

    def start_player_observer(self):
        player_observer_thread_stop_flag = Event()
        player_observer_thread = PlayerObserver(player_observer_thread_stop_flag, self)
        player_observer_thread.name = "player observer"
        player_observer_thread.isDaemon()
        self.player_observer = player_observer_thread
        self.player_observer.start()

    def start_telnet_observer(self):
        tn = Telnet(self.settings.get_setting_by_name(name='telnet_ip'), self.settings.get_setting_by_name(name='telnet_port'), self.settings.get_setting_by_name(name='telnet_password', show_log_init=True))
        telnet_observer_thread_stop_flag = Event()
        telnet_observer_thread = TelnetObserver(telnet_observer_thread_stop_flag, self, tn.tn)
        telnet_observer_thread.name = "telnet observer"
        telnet_observer_thread.isDaemon()
        self.telnet_observer = telnet_observer_thread
        self.telnet_observer.start()

    def has_required_environment(self):
        """ check if needed server-config is available"""
        try:
            server_settings_dict = self.telnet_observer.actions.common.get_active_action_result("system", "gg")
        except Exception as e:
            server_settings_dict = {}
            print("{type}".format(type=type(e)))

        if len(server_settings_dict) > 0:
            we_got_us_some_settings = True
            self.server_settings_dict = server_settings_dict
            # disable polling of the settings, only need 'em once
            self.schedulers_controller["get_game_preferences"]["is_active"] = False
        else:
            we_got_us_some_settings = False
        """ check if required telnet commands are available"""

        try:
            prefix_found = self.telnet_observer.actions.common.get_active_action_result("system", self.settings.get_setting_by_name(name='chatprefix_method'))
        except Exception as e:
            prefix_found = ""
            print("{type}".format(type=type(e)))

        if len(prefix_found) != "":
            have_found_a_sweet_prefix = True
            # disable polling of the settings, only need 'em once
            self.schedulers_controller["set_chat_prefix"]["is_active"] = False
        else:
            have_found_a_sweet_prefix = False

        if we_got_us_some_settings and have_found_a_sweet_prefix:
            result = True
        else:
            result = False

        return result

    def run(self):
        self.is_active = True  # this is set so the main loop can be started / stopped
        self.socketio.emit('server_online', '', namespace='/chrani-bot/public')

        next_cycle = 0
        last_schedule = 0

        while not self.stopped.wait(next_cycle) and self.is_active:
            try:
                profile_start = time.time()
                if not isinstance(self.telnet_observer, TelnetObserver):
                    raise IOError

                self.custodian.check_in('main_loop', True)
                self.time_running = int(time.time() - self.time_launched)

                if not self.has_connection:
                    raise IOError

                has_required_environment = self.has_required_environment()

                if self.schedulers_dict and self.has_connection and timeout_occurred(next_cycle * 10, last_schedule):
                    """ Everything that needs to be checked periodically and is not directly player-related should be done in schedulers
                    """
                    last_schedule = profile_start
                    only_essential = not has_required_environment
                    run_schedulers(self, only_essential=only_essential)

                if not has_required_environment or self.is_paused is not False:
                    time.sleep(self.settings.get_setting_by_name(name='list_players_interval'))
                    continue

                if self.initiate_shutdown is True and self.has_connection:
                    time.sleep(self.settings.get_setting_by_name(name='list_players_interval'))
                    self.is_active = False
                    continue

                lines_processed = self.telnet_observer.execute_queue(10)
                actions_executed = self.player_observer.execute_queue(10)

                self.first_run = False
                self.last_execution_time = time.time() - profile_start
                next_cycle = (0.2 - self.last_execution_time)

            except IOError as error:
                """ clean up bot to have a clean restart when a new connection can be established """
                log_message = "no telnet-connection - trying to connect..."
                self.server_time_running = None

                try:
                    self.start_custodian()
                    self.has_connection = True
                    self.start_telnet_observer()
                    self.socketio.emit('server_online', '', namespace='/chrani-bot/public')

                    self.start_player_observer()
                    self.permissions = Permissions(self.player_observer.actions_list, self.permission_levels_list)

                    self.load_from_db()

                    self.telnet_lines_list = deque()

                    self.reboot_imminent = False
                    self.is_paused = False

                except IOError as e:
                    traceback.print_exc()
                    self.has_connection = False
                    self.first_run = True
                    self.socketio.emit('server_offline', '', namespace='/chrani-bot/public')

                    self.clear_env()
                    log_message = "{} - will try again in {} seconds ({} / {})".format(log_message, str(self.restart_delay), error, e)
                    logger.info(log_message)
                    time.sleep(self.restart_delay)
                    self.restart_delay = 20

            except (NameError, AttributeError) as error:
                traceback.print_exc()
                logger.error("some missing name or attribute error: {} ({})".format(error.message, type(error)))
            except Exception as error:
                traceback.print_exc()
                logger.error("unknown error: {} ({})".format(error.message, type(error)))

        logger.debug("the bots main loop has ended")
        self.shutdown()

    def clear_env(self):
        for player_steamid in self.player_observer.active_player_threads_dict:
            """ kill them ALL! """
            active_player_thread = self.player_observer.active_player_threads_dict[player_steamid]
            active_player_thread["thread"].stopped.set()

        self.telnet_lines_list = deque()
        self.is_paused = True
        try:
            self.telnet_observer.stopped.set()
        except AttributeError:
            pass

        self.telnet_observer = object

    def shutdown(self):
        time.sleep(5)
        self.is_active = False
        self.clear_env()
        self.stopped.set()
        try:
            os._exit(0)
        except SystemExit:
            logger.info("bot has shut down!")