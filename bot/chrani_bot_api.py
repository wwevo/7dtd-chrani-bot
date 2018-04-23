import re
import json
import requests
from urllib import urlencode
from flask import Flask, request, redirect, render_template, send_from_directory, Response
from threading import *
import logging

from bot.websocket_server import WebsocketServer
from bot.panel_user_observer import PanelUserObserver
from bot.assorted_functions import nocache
from bot.logger import logger
import bot.flask_login as flask_login


class ChraniBotApi(Thread):
    bot = object  # holds the running bot object
    app = object  # holds the flask webserver
    ws = object  # holds the websocket-server

    bot_api_url = str

    connected_clients = dict

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event

        self.connected_clients = {}
        self.bot_api_url = "{}://{}".format(self.bot.settings_dict['bot-api_protocol'], self.bot.settings_dict['bot-api_ip'])
        if self.bot.settings_dict['bot-api_port'] is not None:
            self.bot_api_url = "{}:{}".format(self.bot_api_url, self.bot.settings_dict['bot-api_port'])

        self.app = Flask(__name__)
        self.app.secret_key = 'super secret string for' + self.bot.bot_name

        Thread.__init__(self)

    def new_client(self, client, server):
        pass

    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Client({}) disconnected".format(client['id']))

    # Called when a client sends a message
    def message_received(self, client, server, message):
        if client['id'] not in self.connected_clients:
            if message.startswith('connect:'):
                client_steamid = message.partition('connect:')[2]
                self.connected_clients.update({client_steamid: client})

    def run(self):
        app = self.app
        steam_openid_url = 'https://steamcommunity.com/openid/login'

        login_manager = flask_login.LoginManager()
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(login_steamid):
            try:
                player_object = self.bot.players.load(login_steamid)
                if player_object.has_permission_level('authenticated'):
                    return player_object
                else:
                    return None
            except KeyError:
                return None

        @self.app.route("/auth")  # redirects users to the steam-login
        def auth_with_steam():
            params = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': "{}/authorized".format(self.bot_api_url),
                'openid.realm': "{}".format(self.bot_api_url)
            }
            query_string = urlencode(params)
            auth_url = steam_openid_url + "?" + query_string
            return redirect(auth_url)

        @app.route("/authorized")  # exctracts users-info from steam-login response and checks if a local player exists
        @login_manager.request_loader
        def authorized(test=None):
            if test is not None:
                return None
            try:
                login_steamid = re.search(r'http://steamcommunity.com/openid/id/(?P<steamid>.*)', request.args["openid.identity"]).group('steamid')
                player_object = self.bot.players.load(login_steamid)
                flask_login.login_user(player_object)
                panel_user_observer_thread_stop_flag = Event()
                panel_user_observer_thread = PanelUserObserver(panel_user_observer_thread_stop_flag, self, login_steamid)
                panel_user_observer_thread.name = "panel-observer_{})".format(player_object.steamid)  # nice to have for the logs
                panel_user_observer_thread.isDaemon()
                panel_user_observer_thread.start()

                return redirect('/' + login_steamid)
            except Exception as e:
                return redirect('/unauthorized')

        @app.route("/unauthorized")
        @login_manager.unauthorized_handler  # yeah, we don't deal with unauthorized folk at all!
        def unauthorized():
            return render_template('unauthorized.html')

        @app.errorhandler(404)
        def page_not_found(e):
            return redirect('/auth')

        """ API-Endpoints """
        @app.route("/players")
        @flask_login.login_required
        def get_all_players():
            result = {}
            for player_steamid, player_object in self.bot.players.load_all().iteritems():
                result.update({player_steamid: player_object.__dict__})
            return json.dumps(result, indent=4)

        @app.route("/players/<steamid>")
        @flask_login.login_required
        def get_player_by_steamid(steamid):
            result = {}
            try:
                player_object = self.bot.players.load(steamid)
                result.update({steamid: player_object.__dict__})
                return json.dumps(result, indent=4)
            except KeyError:
                return "resource not found"

        @app.route("/players/online")
        @flask_login.login_required
        def get_online_players():
            result = {}
            panel_user_is_online = False
            for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                if player_steamid == flask_login.current_user.steamid:
                    panel_user_is_online = True
                result.update({player_steamid: player_object.__dict__})
            if not panel_user_is_online:
                player_object = self.bot.players.load(flask_login.current_user.steamid)
                result.update({flask_login.current_user.steamid: player_object.__dict__})
            return json.dumps(result, indent=4)

        @app.route("/bases")
        @flask_login.login_required
        def get_player_bases():
            locations_dict = {}
            for location_owner_steamid, location_objects_dict in self.bot.locations.locations_dict.iteritems():
                for location_identifier, location_object in location_objects_dict.iteritems():
                    if location_identifier == 'home':
                        locations_dict.update({location_owner_steamid: location_object.__dict__})
            return json.dumps(locations_dict, indent=4)

        """ Real Routes """
        @app.route('/assets/<path:path>')
        @flask_login.login_required
        def static_assets(path):
            return send_from_directory('templates/assets', path)

        """ remote map-tile loading
        this should only ever be used if there is no other way of obtaining the map-tiles
        the prefered way is to simply use a lcal path to the local map-tiles and set that up in the leaflet directly
        this path is mostly here to enable easy developing, not needing the actual game-server to be present locally
        """
        @app.route('/tiles/<path:path>')
        @flask_login.login_required
        def get_map_tiles(path):
            request_path = '{}/map/{}?adminuser={}&admintoken={}'.format(self.bot.settings_dict['allocs_api_url'], path, self.bot.settings_dict['allocs_api_admin_user'], self.bot.settings_dict['allocs_api_admin_token'])
            pic = requests.get(request_path)
            return Response(pic, mimetype="image/png")

        @app.route("/")
        @flask_login.login_required
        @nocache
        def chrani_bot():
            player_object = flask_login.current_user
            return redirect('/' + player_object.steamid)

        @app.route('/logout')
        @flask_login.login_required
        def logout():
            flask_login.logout_user()
            return redirect('/')

        logger.info("chrani-api started on {}:{}".format(self.bot.settings_dict['bot-api_ip'], self.bot.settings_dict['bot-api_port']))

        ws = WebsocketServer(host="0.0.0.0", port=int(self.bot.settings_dict['bot-api_websocket_port']), loglevel=logging.CRITICAL)
        ws.set_fn_new_client(self.new_client)
        ws.set_fn_client_left(self.client_left)
        ws.set_fn_message_received(self.message_received)
        self.ws = ws
        wst = Thread(target=ws.run_forever, name='websocket')
        wst.daemon = True
        wst.start()

        app.run(host="0.0.0.0", port=self.bot.settings_dict['bot-api_port'])
