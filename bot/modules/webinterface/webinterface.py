import bot.actions
import flask
import flask_login
import flask_socketio
from bot.modules.webinterface.players import get_players_table
from bot.modules.webinterface.system import get_system_status
from bot.modules.webinterface.whitelist import get_whitelist_widget

import re
import os
from urllib import urlencode
import requests
from threading import *


class Webinterface(Thread):
    bot = object
    app = object
    flask = object
    flask_login = object
    flask_socketio = object
    socketio = object

    login_manager = object

    def __init__(self, event, bot):
        template_dir = os.path.join(os.getcwd(), 'templates')
        static_dir = os.path.join(template_dir, 'static')

        self.bot = bot
        self.flask = flask
        self.flask_login = flask_login
        self.flask_socketio = flask_socketio

        self.app = self.flask.Flask(
            __name__,
            template_folder=template_dir,
            static_folder=static_dir
        )
        self.app.config["SECRET_KEY"] = "totallyasecret"

        self.socketio = self.flask_socketio.SocketIO(self.app, async_mode='threading')

        self.login_manager = self.flask_login.LoginManager()
        self.login_manager.init_app(self.app)

        self.stopped = event
        Thread.__init__(self)

    def run(self):
        @self.login_manager.user_loader
        def user_loader(steamid):
            try:
                player_object = self.bot.players.get_by_steamid(steamid)
                if any(x in ["admin", "mod", "donator", "authenticated"] for x in player_object.permission_levels):
                    return player_object
            except:
                return None

        @self.app.route('/login')
        def login():
            steam_openid_url = 'https://steamcommunity.com/openid/login'
            u = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': "http://{}:{}/authenticate".format(self.bot.settings.get_setting_by_name('bot_ip'), self.bot.settings.get_setting_by_name('bot_port')),
                'openid.realm': "http://{}:{}".format(self.bot.settings.get_setting_by_name('bot_ip'), self.bot.settings.get_setting_by_name('bot_port'))
            }
            query_string = urlencode(u)
            auth_url = steam_openid_url + "?" + query_string
            return self.flask.redirect(auth_url)

        @self.app.route('/logout')
        @self.flask_login.login_required
        def logout():
            self.flask_login.logout_user()
            return self.flask.redirect("/")

        @self.app.route('/authenticate', methods=['GET'])
        def setup():
            def validate(signed_params):
                steam_login_url_base = "https://steamcommunity.com/openid/login"
                params = {
                    "openid.assoc_handle": signed_params["openid.assoc_handle"],
                    "openid.sig": signed_params["openid.sig"],
                    "openid.ns": signed_params["openid.ns"],
                    "openid.mode": "check_authentication"
                }

                params_dict = signed_params.to_dict()
                params_dict.update(params)

                params_dict["openid.mode"] = "check_authentication"
                params_dict["openid.signed"] = params_dict["openid.signed"]

                r = requests.post(steam_login_url_base, data=params_dict)

                if "is_valid:true" in r.text:
                    return True

                # this fucntion should always return false if the payload is not valid
                return False

            valid = validate(self.flask.request.args)
            if valid is True:
                p = re.search(r"/(?P<steamid>([0-9]{17}))", str(self.flask.request.args["openid.claimed_id"]))
                if p:
                    steamid = p.group("steamid")
                    try:
                        player_object = self.bot.players.get_by_steamid(steamid)
                        self.flask_login.login_user(player_object, remember=True)
                        return self.flask.redirect("/protected")
                    except:
                        pass

            return self.flask.redirect("/")

        @self.app.route('/unauthorized')
        @self.login_manager.unauthorized_handler
        def unauthorized_handler():
            output = 'You are not authorized. You need to be authenticated in-game to get access to the webinterface ^^<br />'
            output += '<a href="/">home</a><br /><br />'
            markup = self.flask.Markup(output)
            return self.flask.render_template('index.html', bot=self.bot, content=markup)

        @self.app.errorhandler(404)
        def page_not_found(error):
            output = 'Page not found :(<br />'
            output += '<a href="/">home</a><br /><br />'
            markup = self.flask.Markup(output)
            return self.flask.render_template('index.html', bot=self.bot, content=markup), 404

        @self.app.route('/')
        def index():
            if self.flask_login.current_user.is_authenticated is True:
                return self.flask.redirect("/protected")

            output = "Welcome to the <strong>{}</strong><br />".format(self.bot.name)

            markup = self.flask.Markup(output)
            system_status_widget = get_system_status()
            return self.flask.render_template('index.html', bot=self.bot, content=markup, system_status_widget=system_status_widget)

        @self.app.route('/protected')
        @self.flask_login.login_required
        def protected():
            output = get_players_table()

            markup = self.flask.Markup(output)
            system_status_widget = get_system_status()
            whitelist_widget = get_whitelist_widget()
            return self.flask.render_template('index.html', bot=self.bot, content=markup, system_status_widget=system_status_widget, whitelist_widget=whitelist_widget)

        """ collecting all defined actions and creating routes for them """
        for actions_list_entry in bot.modules.webinterface.actions_list:
            if actions_list_entry['authenticated'] is True:
                action = actions_list_entry['action']
                wrapped_action = self.flask_login.login_required(action)
                self.app.add_url_rule(actions_list_entry['route'], view_func=wrapped_action)
            else:
                action = actions_list_entry['action']
                self.app.add_url_rule(actions_list_entry['route'], view_func=action)

        self.socketio.run(self.app, host='0.0.0.0', port=5000)
