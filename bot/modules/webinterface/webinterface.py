import bot.actions
import bot.external.flask as flask
import bot.external.flask_login as flask_login
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
    login_manager = object

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        template_dir = os.path.join(os.getcwd(), 'templates')
        static_dir = os.path.join(template_dir, 'static')

        self.flask = flask

        app = self.flask.Flask(
            __name__,
            template_folder=template_dir,
            static_folder=static_dir
        )
        self.app = app
        self.app.config["SECRET_KEY"] = "totallyasecret"

        self.flask_login = flask_login

        login_manager = self.flask_login.LoginManager()
        self.login_manager = login_manager
        self.login_manager.init_app(app)

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
            return self.flask.render_template('index.html', bot=self.bot, content=markup)

        @self.app.route('/protected')
        @self.flask_login.login_required
        def protected():
            player_objects_to_list = self.bot.players.get_all_players(get_online_only=True)
            output = self.flask.render_template('online_players.html', player_objects_to_list=player_objects_to_list)

            output += '<hr/>'
            player_objects_to_list = self.bot.players.get_all_players()
            player_locations_to_list = {}
            player_groups_to_list = {}
            for player_object in player_objects_to_list:
                player_locations = []
                for location_identifier, location_object in self.bot.locations.get(player_object.steamid).iteritems():
                    player_locations.append(location_object)

                try:
                    player_locations_to_list.update({player_object.steamid: player_locations})
                except:
                    player_locations_to_list = {player_object.steamid: player_locations}

                player_groups = []
                for permission_level in self.bot.permission_levels_list:
                    if player_object.has_permission_level(permission_level):
                        href = "/protected/authentication/remove/group/{}/{}".format(player_object.steamid, permission_level)
                        player_groups.append(self.flask.Markup(self.flask.render_template('link_active.html', href=href, text=permission_level)))
                    else:
                        href = "/protected/authentication/add/group/{}/{}".format(player_object.steamid, permission_level)
                        player_groups.append(self.flask.Markup(self.flask.render_template('link_inactive.html', href=href, text=permission_level)))

                try:
                    player_groups_to_list.update({player_object.steamid: player_groups})
                except:
                    player_groups_to_list = {player_object.steamid: player_groups}

            output += self.flask.render_template('all_players.html', player_objects_to_list=player_objects_to_list, player_locations_to_list=player_locations_to_list, player_groups_to_list=player_groups_to_list)

            markup = self.flask.Markup(output)
            return self.flask.render_template('index.html', bot=self.bot, content=markup)

        for actions_list_entry in bot.modules.webinterface.actions_list:
            if actions_list_entry['authenticated'] is True:
                action = actions_list_entry['action']
                wrapped_action = self.flask_login.login_required(action)
                self.app.add_url_rule(actions_list_entry['route'], view_func=wrapped_action)
            else:
                action = actions_list_entry['action']
                self.app.add_url_rule(actions_list_entry['route'], view_func=action)

        self.app.run(
            host=self.bot.settings.get_setting_by_name('bot_ip'),
            port=self.bot.settings.get_setting_by_name('bot_port'),
            use_reloader=False, # makes flasks debug mode work
            debug=True
        )
