import traceback
from threading import *
import time
import math
import os

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

    app = object
    flask = object
    flask_login = object
    socketio = object

    stopped = object

    is_paused = bool  # used to pause all processing without shutting down the bot

    initiate_shutdown = bool

    match_types = dict
    match_types_generic = dict

    first_run = bool
    last_execution_time = float
    restart_delay = int
    reboot_imminent = bool
    telnet_queue = int

    passwords = dict
    banned_countries_list = list

    settings_dict = dict

    players = object
    locations = object
    whitelist = object
    webinterface = object
    permissions = object
    permission_levels_list = list
    settings = object
    telnet_observer = object
    player_observer = object
    custodian = object

    observers_dict = dict
    observers_controller = dict
    actions_list = list
    schedulers_dict = dict
    schedulers_controller = dict

    def __init__(self, app, flask, flask_login, socketio):
        self.app = app
        self.flask = flask
        self.flask_login = flask_login
        self.socketio = socketio

        self.stopped = Event()
        Thread.__init__(self)

    def setup(self):
        self.name = 'chrani-bot'
        self.settings = Settings(self)
        self.dom = {
            "bot_name": self.settings.get_setting_by_name(name='bot_name', default='chrani_bot'),
            "bot_version": self.settings.get_setting_by_name(name='bot_version', default='0.7.835'),
            "bot_flags": {
                "bot_has_working_environment": False,
                "telnet_is_available": False,
                "has_database_available": False
            },
            "bot_data": {
                "active_threads": {
                    "schedulers_system": {},
                    "modules": {},
                    "actions": {},
                    "player_observer": {}
                },
                "telnet_observer": {},
                "time_launched": None,
                "time_running": None,
                "settings": {
                    "color_scheme": self.settings.get_setting_by_name(name='chatbox_color_scheme', default={
                        "standard": "afb0b2",
                        "highlight": "b3b8bc",
                        "header": "e57255",
                        "warning": "e5c453",
                        "success": "52d273",
                        "error": "e95065",
                        "info": "46bddf"
                    })
                },
                "player_data": {
                    "system": {
                        "name": "system",
                        "steamid": -1,
                    }
                },
                "location_data": {}
            },
            "game_data": {
                "settings": {},
                "gametime": None,
                "time_running": None,
                "restart_in": None,
                "landclaim_data": {}
            },
        }

        self.is_paused = False
        self.reboot_imminent = False
        self.initiate_shutdown = False
        self.restart_delay = 0
        self.first_run = True
        self.last_execution_time = 0.0
        self.telnet_queue = 0

        logger.info("{} started".format(self.dom['bot_name']))

        self.players = Players(self)

        self.observers_dict = global_observer.observers_dict
        self.observers_controller = global_observer.observers_controller

        self.schedulers_dict = global_scheduler.schedulers_dict
        self.schedulers_controller = global_scheduler.schedulers_controller

        self.whitelist = Whitelist(self)
        if self.settings.get_setting_by_name(name='whitelist_active') is not False:
            self.whitelist.activate()

        self.locations = Locations(self)

        self.passwords = self.settings.get_setting_by_name(name='authentication_groups', default={
            "admin": "changeme",
            "mod": "changeme",
            "donator": "changeme",
            "authenticated": "changeme"
        })

        self.permission_levels_list = self.passwords.keys()  # ['admin', 'mod', 'donator', 'authenticated']

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
        self.permissions = Permissions(self, self.permission_levels_list)
        return self

    def start(self):
        logger.info("{} started".format(self.name))
        self.dom["bot_data"]["time_launched"] = time.time()
        self.socketio.emit('server_online', '', namespace='/chrani-bot/public')
        self.custodian = Custodian(self).setup().start()

        self.player_observer = PlayerObserver(self).setup().start()

        if not self.dom.get("bot_flags").get("has_database_available", False):
            self.load_local_files()

        Thread.start(self)
        return self

    def load_local_files(self):
        self.settings.load_all()
        self.players.load_all()
        self.locations.load_all()  # load all location data to memory
        self.whitelist.load_all()  # load all whitelisted players
        self.permissions.load_all(self.player_observer.actions_list)  # get the permissions or create new permissions-file
        self.dom["bot_flags"]["has_database_available"] = True

    def manage_landclaims(self):
        polled_lcb = self.telnet_observer.actions.get_active_action_result('system', self.settings.get_setting_by_name(name='listlandprotection_method', default='llp'))
        if len(polled_lcb) >= 1 and polled_lcb != self.dom["game_data"]["landclaim_data"]:
            self.dom["game_data"]["landclaim_data"] = polled_lcb
            lcb_owners_to_delete = {}
            lcb_owners_to_update = {}
            lcb_owners_to_update.update(self.dom["game_data"]["landclaim_data"])
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
            land_claim_size = int(self.dom["game_data"]["settings"]["LandClaimSize"])
        except (KeyError, TypeError) as error:
            return lcb_list_final

        try:
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
        except AttributeError as e:
            pass

        return lcb_list_final

    def landclaims_find_by_distance(self, start_coords, distance_in_blocks):
        landclaims_in_reach_list = []
        landclaims_dict = self.dom["game_data"]["landclaim_data"]
        for player_steamid, landclaims in landclaims_dict.iteritems():
            for landclaim in landclaims:
                distance = math.sqrt((float(landclaim[0]) - float(start_coords[0]))**2 + (float(landclaim[1]) - float(start_coords[1]))**2 + (float(landclaim[2]) - float(start_coords[2]))**2)
                if distance < distance_in_blocks:
                    landclaims_in_reach_list.append({player_steamid: landclaim})

        return landclaims_in_reach_list

    def check_for_homes(self, player_object):
        distance = math.floor(int(self.dom["game_data"]["settings"]['LandClaimSize']) / 2) + int(self.dom["game_data"]["settings"]['LandClaimDeadZone'])  # (landclaim size / 2) + Deadzone
        start_coords = player_object.get_coord_tuple()

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
        gametime = self.dom.get("game_data").get("gametime", None)
        if gametime is None or len(gametime) <= 0:
            return False

        gameday = gametime.get("day", None)
        gamehour = gametime.get("hour", None)
        gameminute = gametime.get("minute", None)

        if (gameday is None or len(gameday) <= 0) or (gamehour is None or len(gamehour) <= 0):
            return False

        bloodmoon = False
        if self.is_it_horde_day(int(gameday)) and int(gamehour) >= 21:
            bloodmoon = True

        day_after_bloodmoon = False
        if self.is_it_horde_day(int(gameday) - 1) and int(gamehour) < 4:
            day_after_bloodmoon = True

        if bloodmoon or day_after_bloodmoon:
            return True

        return False

    def has_required_environment(self):
        """ check if needed server-config is available"""
        try:
            server_settings_dict = self.telnet_observer.actions.common.get_active_action_result("system", "gg")
        except Exception as e:
            server_settings_dict = {}
            print("{type}".format(type=type(e)))

        if len(server_settings_dict) > 0:
            we_got_us_some_settings = True
            self.dom["game_data"]["settings"] = server_settings_dict
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
        next_cycle = 0
        last_schedule = 0
        while not self.stopped.wait(next_cycle):
            try:
                profile_start = time.time()
                self.dom["bot_data"]["time_running"] = int(time.time() - self.dom["bot_data"]["time_launched"])
                self.custodian.check_in('main_loop', True)

                """ everything that needs to be checked periodically and is not directly player-related should be done in schedulers
                """
                if self.schedulers_dict and timeout_occurred(max(math.fabs(next_cycle * 10), 2), last_schedule):
                    last_schedule = profile_start
                    only_essential = not self.dom.get("bot_flags").get("bot_has_working_environment")
                    run_schedulers(self, only_essential=only_essential)

                if not isinstance(self.telnet_observer, TelnetObserver) or self.telnet_observer.stopped.isSet():
                    try:
                        telnet = Telnet(
                            self.settings.get_setting_by_name(name='telnet_ip', default="127.0.0.1"),
                            self.settings.get_setting_by_name(name='telnet_port', default="8082"),
                            self.settings.get_setting_by_name(name='telnet_password', default="setmeinconfigfile",
                                                              show_log_init=True)
                        )
                        self.telnet_observer = TelnetObserver(self, telnet.authenticated_connection).setup().start()
                        self.dom["bot_flags"]["telnet_is_available"] = True
                        self.socketio.emit('server_online', '', namespace='/chrani-bot/public')

                        self.reboot_imminent = False
                        self.is_paused = False

                    except IOError as e:
                        # traceback.print_exc()
                        self.clear_env()
                        self.socketio.emit('server_offline', '', namespace='/chrani-bot/public')
                        log_message = "no telnet-connection - trying to connect... - will try again in {} seconds ({})".format(str(self.restart_delay), e)
                        logger.info(log_message)
                        time.sleep(self.restart_delay)
                        self.restart_delay = 20
                        continue

                if not self.dom.get("bot_flags").get("bot_has_working_environment", False):
                    self.dom["bot_flags"]["bot_has_working_environment"] = self.has_required_environment()

                """ this check has to be after schedulers are run, since those actually initialize the environment """
                if not self.dom.get("bot_flags").get("bot_has_working_environment", False) or self.is_paused is not False:
                    time.sleep(self.settings.get_setting_by_name(name='list_players_interval'))
                    continue

                if self.initiate_shutdown is True:
                    time.sleep(self.settings.get_setting_by_name(name='list_players_interval'))
                    self.stopped.set()
                    continue

                """" for now i'm doing 20 at a time to preven clogging, don't have the data yet to actually show that it would otherwise
                """
                lines_processed = self.telnet_observer.execute_queue(20)
                actions_executed = self.player_observer.execute_queue(20)

                self.first_run = False
                self.last_execution_time = time.time() - profile_start
                next_cycle = math.fabs(0.2 - self.last_execution_time)

            except (NameError, AttributeError) as error:
                traceback.print_exc()
                logger.error("some missing name or attribute error: {} ({})".format(error.message, type(error)))
            except IOError as error:
                """ clean up bot to have a clean restart when a new connection can be established """
                pass
            except Exception as error:
                traceback.print_exc()
                logger.error("unknown error: {} ({})".format(error.message, type(error)))

        logger.debug("the bots main loop has ended")
        self.shutdown()

    def clear_env(self):
        self.dom["game_data"]["gametime"] = None
        self.dom["game_data"]["time_running"] = None
        self.dom["game_data"]["restart_in"] = None
        self.dom["bot_flags"]["telnet_is_available"] = False
        self.first_run = True
        self.is_paused = True

    def shutdown(self):
        time.sleep(5)
        self.custodian.stopped.set()
        self.clear_env()
        self.stopped.set()
        try:
            os._exit(0)
        except SystemExit:
            logger.info("bot has shut down!")