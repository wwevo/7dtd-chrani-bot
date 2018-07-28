import os
from urllib import urlencode
import flask
import flask_login
import re
from threading import *


class Webinterface(Thread):
    bot = object
    app = object

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        steam_openid_url = 'https://steamcommunity.com/openid/login'
        template_dir = self.bot.app_root + '/data/templates'

        app = flask.Flask(self.bot.name + " webservice", template_folder=template_dir)
        app.secret_key = 'super secret string'  # Change this!
        bot_ip = self.bot.settings.get_setting_by_name('bot_ip')
        bot_port = self.bot.settings.get_setting_by_name('bot_port')

        login_manager = flask_login.LoginManager()
        login_manager.init_app(app)

        @login_manager.user_loader
        def user_loader(steamid):
            try:
                player_object = self.bot.players.get_by_steamid(steamid)
                if any(x in ["admin", "mod", "donator", "authenticated"] for x in player_object.permission_levels):
                    return player_object
            except:
                return None

        @app.route('/')
        def index():
            authenticated = flask_login.current_user.is_authenticated
            if authenticated:
                return flask.render_template("webinterface/index.html", authenticated=True, bot=self.bot, player_object=flask_login.current_user, logout_url="/logout")
            else:
                return flask.render_template("webinterface/index.html", authenticated=False, bot=self.bot, login_url="/login")

        @app.route('/login')
        def login():
            params = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': 'http://' + bot_ip + ':' + str(bot_port) + '/authorize',
                'openid.realm': 'http://' + bot_ip + ':' + str(bot_port)
            }

            query_string = urlencode(params)
            auth_url = steam_openid_url + "?" + query_string
            return flask.redirect(auth_url)

        @app.route('/authorize')
        def authorize():
            p = re.search(r"/(?P<steamid>([0-9]{17}))", str(flask.request.args["openid.claimed_id"]))
            if p:
                steamid = p.group("steamid")
                try:
                    player_object = self.bot.players.get_by_steamid(steamid)
                    status = flask_login.login_user(player_object)
                    return flask.redirect("/")
                except:
                    pass

            return flask.redirect('/unauthorized')

        @app.route('/logout')
        def logout():
            flask_login.logout_user()
            return flask.redirect('/')

        @app.route('/shutdown')
        @flask_login.login_required
        def shutdown():
            func = flask.request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            self.bot.shutdown()
            return flask.redirect("/logout")

        @app.route('/unauthorized')
        @login_manager.unauthorized_handler
        def unauthorized_handler():
            return flask.render_template("webinterface/unauthorized.html", bot=self.bot, login_url="/login")

        app.run(host=bot_ip)
