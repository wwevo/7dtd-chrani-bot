from threading import Thread
from flask import Flask, request, redirect, render_template, send_from_directory, Response
import requests
import bot.flask_login as flask_login
from urllib import urlencode
import re
from logger import logger
import logging
import time
import json


class ChraniBotApi(Thread):
    bot = object

    def __init__(self, bot, event):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        app = Flask(__name__)
        app.secret_key = 'super secret string'

        login_manager = flask_login.LoginManager()
        login_manager.init_app(app)

        steam_openid_url = 'https://steamcommunity.com/openid/login'
        logger.info("chrani-api started on {}:{}".format(self.bot.panel_url, self.bot.panel_port))

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

        @app.route("/auth")  # redirects users to the steam-login
        def auth_with_steam():
            params = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': "{}://{}:{}/authorized".format(self.bot.panel_protocol, self.bot.panel_url, self.bot.panel_port),
                'openid.realm': "{}://{}:{}".format(self.bot.panel_protocol, self.bot.panel_url, self.bot.panel_port)
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
                return redirect('/')
            except Exception as e:
                return redirect('/unauthorized')

        @login_manager.unauthorized_handler  # yeah, we don't deal with unauthorized folk at all!
        def unauthorized():
            return render_template('unauthorized.html')

        """ API-Endpoints """
        @app.route("/me")
        @flask_login.login_required
        def whoami():
            player_object = flask_login.current_user
            return player_object.steamid

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
            for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                result.update({player_steamid: player_object.__dict__})
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

        @app.route('/tiles/<path:path>')
        @flask_login.login_required
        def get_map_tiles(path):
            request_path = 'http://panel.chrani-bot.notjustfor.me:8082/map/{}?adminuser={}&admintoken={}'.format(path, 'chrani_bot_panel', 'totally_secure_321')
            pic = requests.get(request_path)
            return Response(pic, mimetype="image/png")

        @app.route("/")
        @flask_login.login_required
        def chrani_bot():
            leaflet_head = ""
            leaflet_map = ""
            player_object = flask_login.current_user
            if player_object.has_permission_level("authenticated"):
                leaflet_head = render_template('leaflet_head_tilelayer.html')
                leaflet_map = render_template('leaflet_map_tilelayer.html', panel_user_steamid=player_object.steamid)
                leaflet_map += render_template('leaflet_map_playerlayer.html')
                leaflet_map += render_template('leaflet_map_baseslayer.html')
            if player_object.has_permission_level("moderator") or player_object.has_permission_level("admin"):
                leaflet_map += render_template('leaflet_map_locationlayer.html')
                leaflet_map += render_template('leaflet_map_lcblayer.html')

            return render_template('index.html', player_name=player_object.name, head=leaflet_head, main=leaflet_map)

        @app.route('/logout')
        @flask_login.login_required
        def logout():
            flask_login.logout_user()
            return redirect('/')

        # app.logger.disabled = True
        # log = logging.getLogger('werkzeug')
        # log.disabled = True
        app.run(host=self.bot.panel_url, port=self.bot.panel_port)


