import bot.actions
import flask
import flask_login
import time
import re
import os
import datetime
from urllib import urlencode
import requests
from threading import *


class Webinterface(Thread):
    bot = object
    app = object

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        template_dir = os.path.join(os.getcwd(), 'templates')
        static_dir = os.path.join(template_dir, 'static')

        app = flask.Flask(
            __name__,
            template_folder=template_dir,
            static_folder=static_dir
        )
        app.config["SECRET_KEY"] = "totallyasecret"

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

        @app.route('/login')
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
            return flask.redirect(auth_url)

        @app.route("/logout")
        @flask_login.login_required
        def logout():
            flask_login.logout_user()
            return flask.redirect("/")

        @app.route('/authenticate', methods=['GET'])
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

            valid = validate(flask.request.args)
            if valid is True:
                p = re.search(r"/(?P<steamid>([0-9]{17}))", str(flask.request.args["openid.claimed_id"]))
                if p:
                    steamid = p.group("steamid")
                    try:
                        player_object = self.bot.players.get_by_steamid(steamid)
                        flask_login.login_user(player_object, remember=True)
                        return flask.redirect("/protected")
                    except:
                        pass

            return flask.redirect("/")

        @app.route('/protected/system/pause')
        @flask_login.login_required
        def pause_bot():
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            bot.actions.common.trigger_action(self.bot, player_object, player_object, "pause bot")
            response = {
                "actionResponse": "{} has been paused".format(self.bot.name),
                "actionResult": True
            }

            if flask.request.accept_mimetypes.best == 'application/json':
                return app.response_class(
                    response=flask.json.dumps(response),
                    mimetype='application/json'
                )
            else:
                return flask.redirect("/protected?{}".format(urlencode(response)))

        @app.route('/protected/system/resume')
        @flask_login.login_required
        def resume_bot():
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            bot.actions.common.trigger_action(self.bot, player_object, player_object, "resume bot")
            response = {
                "actionResponse": "{} has been resumed".format(self.bot.name),
                "actionResult": True
            }
            if flask.request.accept_mimetypes.best == 'application/json':
                return app.response_class(
                    response=flask.json.dumps(response),
                    mimetype='application/json'
                )
            else:
                return flask.redirect("/protected?{}".format(urlencode(response)))

        @app.route('/protected/system/shutdown')
        @flask_login.login_required
        def shutdown():
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            bot.actions.common.trigger_action(self.bot, player_object, player_object, "shut down the matrix")
            response = {
                "actionResponse": "{} has been shut down".format(self.bot.name),
                "actionResult": True
            }
            if flask.request.accept_mimetypes.best == 'application/json':
                return app.response_class(
                    response=flask.json.dumps(response),
                    mimetype='application/json'
                )
            else:
                return flask.redirect("/protected?{}".format(urlencode(response)))

        @app.route('/protected/players/kick/<steamid>/<reason>')
        @flask_login.login_required
        def kick_player(steamid, reason):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            bot.actions.common.trigger_action(self.bot, player_object, target_player, "kick player {} for {}".format(steamid, reason))
            return flask.redirect("/protected")

        @app.route('/protected/players/obliterate/<steamid>')
        @flask_login.login_required
        def obliterate_player(steamid):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            bot.actions.common.trigger_action(self.bot, player_object, target_player, "obliterate player {}".format(steamid))
            return flask.redirect("/protected")

        @app.route('/protected/authentication/add/group/<steamid>/<group>')
        @flask_login.login_required
        def add_player_to_group(steamid, group):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            bot.actions.common.trigger_action(self.bot, player_object, target_player, "add player {} to group {}".format(steamid, group))
            return flask.redirect("/protected")

        @app.route('/protected/authentication/remove/group/<steamid>/<group>')
        @flask_login.login_required
        def remove_player_from_group(steamid, group):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            bot.actions.common.trigger_action(self.bot, player_object, target_player, "remove player {} from group {}".format(steamid, group))
            return flask.redirect("/protected")

        @app.route('/protected/players/send/<steamid>/home')
        @flask_login.login_required
        def send_player_home(steamid):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            try:
                location_object = self.bot.locations.get(steamid, 'home')
                pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
                coord_tuple = (pos_x, pos_y, pos_z)
                bot.actions.common.trigger_action(self.bot, player_object, target_player, "send player {} to {}".format(steamid, str(coord_tuple)))
            except:
                pass

            return flask.redirect("/protected")

        @app.route('/protected/players/send/<steamid>/to/lobby')
        @flask_login.login_required
        def send_player_to_lobby(steamid):
            player_object = self.bot.players.get_by_steamid(flask_login.current_user.steamid)
            target_player = self.bot.players.get_by_steamid(steamid)
            try:
                location_object = self.bot.locations.get('system', 'lobby')
                pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
                coord_tuple = (pos_x, pos_y, pos_z)
                bot.actions.common.trigger_action(self.bot, player_object, target_player, "send player {} to {}".format(steamid, str(coord_tuple)))
            except:
                pass

            return flask.redirect("/protected")

        @app.route('/')
        def hello_world():
            if self.bot.is_paused is True:
                bot_paused_status = "paused"
            else:
                bot_paused_status = "active"

            time_running_seconds = int(time.time() - self.bot.time_launched)
            time_running = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=time_running_seconds)

            output = "Welcome to the <strong>{}</strong><br />".format(self.bot.name)
            output += "I have been running for <strong>{}</strong> and am currently <strong>{}</strong><br />".format("{}d, {}h{}m{}s".format(time_running.day-1, time_running.hour, time_running.minute, time_running.second), bot_paused_status)
            output += "I have <strong>{} players</strong> on record and manage <strong>{} locations</strong>.<br /><br />".format(len(self.bot.players.players_dict), sum(len(v) for v in self.bot.locations.all_locations_dict.itervalues()))
            output += '<a href="/login">log in with your steam-account</a>'

            markup = flask.Markup(output)
            return flask.render_template('index.html', bot=self.bot, content=markup)

        @app.route('/protected')
        @flask_login.login_required
        def protected():
            if self.bot.is_paused is True:
                bot_paused_status = "paused"
            else:
                bot_paused_status = "active"

            output = 'Hello <strong>{}</strong><br /><br />'.format(flask_login.current_user.name)
            output += "Welcome to the protected area<br />"
            output += '<a href="/protected/system/pause" onclick="apicall(this); return false;">pause</a>, <a href="/protected/system/resume" onclick="apicall(this); return false;">resume</a>: '
            output += 'the bot is currently <strong>{}</strong>!<br /><br />'.format(bot_paused_status)

            output += '<hr/>'
            player_objects_to_list = self.bot.players.get_all_players(get_online_only=True)
            output += flask.render_template('online_players.html', player_objects_to_list=player_objects_to_list)

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
                        player_groups.append(flask.Markup(flask.render_template('link_active.html', href=href, text=permission_level)))
                    else:
                        href = "/protected/authentication/add/group/{}/{}".format(player_object.steamid, permission_level)
                        player_groups.append(flask.Markup(flask.render_template('link_inactive.html', href=href, text=permission_level)))

                try:
                    player_groups_to_list.update({player_object.steamid: player_groups})
                except:
                    player_groups_to_list = {player_object.steamid: player_groups}

            output += flask.render_template('all_players.html', player_objects_to_list=player_objects_to_list, player_locations_to_list=player_locations_to_list, player_groups_to_list=player_groups_to_list)

            output += '<hr/>'
            output += '<a href="/logout">logout user {}</a><br /><br />'.format(flask_login.current_user.name)
            output += '<a href="/protected/system/shutdown" onclick="apicall(this); return false;">shutdown bot</a><br /><br />'

            markup = flask.Markup(output)
            return flask.render_template('index.html', bot=self.bot, content=markup)

        @app.route('/unauthorized')
        @login_manager.unauthorized_handler
        def unauthorized_handler():
            output = 'You are not authorized. You need to be authenticated in-game to get access to the webinterface ^^<br />'
            output += '<a href="/">home</a><br /><br />'
            markup = flask.Markup(output)
            return flask.render_template('index.html', bot=self.bot, content=markup)

        @app.errorhandler(404)
        def page_not_found(error):
            output = 'Page not found :(<br />'
            output += '<a href="/">home</a><br /><br />'
            markup = flask.Markup(output)
            return flask.render_template('index.html', bot=self.bot, content=markup), 404

        app.run(
            host=self.bot.settings.get_setting_by_name('bot_ip'),
            port=self.bot.settings.get_setting_by_name('bot_port'),
            use_reloader=False, # makes flasks debug mode work
            debug=True
        )
