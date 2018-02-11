from threading import Thread
from flask import Flask, request, redirect, session
import flask_login
import requests
from urllib import urlencode, quote
import re
from logger import logger

import logging
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
        server_ip = "0.0.0.0"
        server_port = int(self.bot.server_settings_dict["Server-Port"]) -1
        logger.info("chrani-api started on {}:{}".format(server_ip, server_port))

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

        @app.route("/authorized")
        @login_manager.request_loader
        def authorized(test=None):
            if test is not None:
                return None
            try:
                login_steamid = re.search(r'http://steamcommunity.com/openid/id/(?P<steamid>.*)', request.args["openid.identity"]).group('steamid')
                player_object = self.bot.players.load(login_steamid)
                flask_login.login_user(player_object)
                return redirect('/panel')
            except Exception as e:
                return None

        @app.route("/auth")
        def auth_with_steam():
            params = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': 'http://127.0.0.1:26899/authorized',
                'openid.realm': 'http://127.0.0.1:26899'
            }
            query_string = urlencode(params)
            auth_url = steam_openid_url + "?" + query_string
            return redirect(auth_url)

        @app.route("/players")
        def get_all_players():
            key = request.headers.get('X-API-KEY')
            if key == "612e648bf9594adb50844cad6895f2cf":
                result = {}
                for player_steamid, player_object in self.bot.players.load_all().iteritems():
                    result.update({player_steamid: player_object.__dict__})
                return json.dumps(result, indent=4)
            else:
                return "access denied"

        @app.route("/players/online")
        def get_online_players():
            key = request.headers.get('X-API-KEY')
            if key == "612e648bf9594adb50844cad6895f2cf":
                result = {}
                for player_steamid, player_object in self.bot.players.players_dict.iteritems():
                    result.update({player_steamid: player_object.__dict__})
                return json.dumps(result, indent=4)
            else:
                return "access denied"

        @app.route("/bases")
        def get_player_bases():
            key = request.headers.get('X-API-KEY')
            if key == "612e648bf9594adb50844cad6895f2cf":
                locations_dict = {}
                for location_owner_steamid, location_objects_dict in self.bot.locations.locations_dict.iteritems():
                    for location_identifier, location_object in location_objects_dict.iteritems():
                        if location_identifier == 'home':
                            locations_dict.update({location_owner_steamid: location_object.__dict__})
                return json.dumps(locations_dict, indent=4)
            else:
                return "access denied"

        @app.route("/")
        def chrani_bot():
            return '<a href="/auth">Login with steam</a>'

        @login_manager.unauthorized_handler
        def unauthorized():
            return "You need to have logged in on the server at least once and must also be an authenticated player to get access to the panel ^^"

        @app.route("/panel")
        @flask_login.login_required
        def chrani_panel():
            player_object = flask_login.current_user
            output = "Hello {}. It's good to see you!".format(player_object.name)
            return output

        @app.route('/logout')
        def logout():
            flask_login.logout_user()
            return 'Logged out'

        # app.logger.disabled = True
        # log = logging.getLogger('werkzeug')
        # log.disabled = True
        app.run(host=server_ip, port=server_port)


