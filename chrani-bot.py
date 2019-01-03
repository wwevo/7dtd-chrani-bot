import os
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

try:
    from is_local import is_debug
    debug = is_debug
except ImportError:
    debug = False

import re
import requests
from urllib import urlencode
from threading import *

if not debug:
    import eventlet
    eventlet.monkey_patch()

import flask
import flask_login
import flask_socketio

template_dir = os.path.join(os.getcwd(), 'templates')
static_dir = os.path.join(template_dir, 'static')

from bot.chrani_bot import ChraniBot
from bot.webinterface.settings import get_settings_general_widget
from bot.webinterface.settings import get_settings_scheduler_widget
from bot.webinterface.settings import get_settings_player_observer_widget
from bot.webinterface.players import get_player_table_widget
from bot.webinterface.system import get_system_status
from bot.webinterface.system import get_command_log_widget
from bot.webinterface.system import get_status_log_widget
from bot.webinterface.system import get_system_health_widget

from bot.webinterface.whitelist import get_whitelist_widget
from bot.webinterface.system import get_banned_players_widget
from bot.webinterface.system import get_map_widget
from bot.webinterface import actions_list

from bot.objects.player import Player

if __name__ == '__main__':
    app = flask.Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.config["SECRET_KEY"] = "totallyasecret"

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    if not debug:
        socketio = flask_socketio.SocketIO(app, async_mode='eventlet')
    else:
        socketio = flask_socketio.SocketIO(app, async_mode='threading')

    chrani_bot_thread_stop_flag = Event()
    chrani_bot = ChraniBot(chrani_bot_thread_stop_flag, app, flask, flask_login, socketio)
    chrani_bot.start()

    @login_manager.user_loader
    def user_loader(steamid):
        try:
            player_object = chrani_bot.players.get_by_steamid(steamid)
            if player_object.steamid in chrani_bot.settings.get_setting_by_name(name='webinterface_admins') or chrani_bot.whitelist.player_is_allowed(player_object):
                return player_object
        except:
            player_dict = {
                "steamid": steamid,
                "name": "system",
            }

            player_object = Player(**player_dict)
            chrani_bot.players.upsert(player_object)
            player_object.add_permission_level("admin")
            return player_object

    @app.route('/login')
    def login():
        steam_openid_url = 'https://steamcommunity.com/openid/login'
        u = {
            'openid.ns': "http://specs.openid.net/auth/2.0",
            'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
            'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
            'openid.mode': 'checkid_setup',
            'openid.return_to': "http://{}:{}/authenticate".format(chrani_bot.settings.get_setting_by_name(name='bot_ip'), chrani_bot.settings.get_setting_by_name(name='bot_port')),
            'openid.realm': "http://{}:{}".format(chrani_bot.settings.get_setting_by_name(name='bot_ip'), chrani_bot.settings.get_setting_by_name(name='bot_port'))
        }
        query_string = urlencode(u)
        auth_url = "{}?{}".format(steam_openid_url, query_string)
        return flask.redirect(auth_url)


    @app.route('/logout')
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

            # this fucntion should always return False if the payload is not valid
            return False

        valid = validate(flask.request.args)
        if valid is True:
            p = re.search(r"/(?P<steamid>([0-9]{17}))", str(flask.request.args["openid.claimed_id"]))
            if p:
                steamid = p.group("steamid")
                try:
                    player_object = chrani_bot.players.get_by_steamid(steamid)
                except:
                    player_dict = {
                        "steamid": steamid,
                        "name": "system",
                    }

                    player_object = Player(**player_dict)
                    chrani_bot.players.upsert(player_object)
                    player_object.add_permission_level("admin")

                flask_login.login_user(player_object, remember=True)
                return flask.redirect("/protected")

        return flask.redirect("/")


    @app.route('/unauthorized')
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        output = 'You are not authorized. You need to be authenticated in-game to get access to the webinterface ^^<br />'
        output += '<a href="/">home</a><br /><br />'
        markup = flask.Markup(output)
        return flask.render_template('index.html', chrani_bot=chrani_bot, content=markup)


    @app.errorhandler(404)
    def page_not_found(error):
        output = 'Page not found :(<br />'
        output += '<a href="/">home</a><br /><br />'
        markup = flask.Markup(output)
        return flask.render_template('index.html', chrani_bot=chrani_bot, content=markup), 404


    @app.route('/')
    def index():
        if flask_login.current_user.is_authenticated is True:
            return flask.redirect("/protected")

        output = '<div class="widget wide">'
        output += "Welcome to the <strong>{}</strong><br />".format(chrani_bot.dom['bot_name'])
        output += "</div>"

        markup = flask.Markup(output)
        system_status_widget = get_system_status()
        return flask.render_template('index.html', chrani_bot=chrani_bot, content=markup, system_status_widget=system_status_widget)


    @app.route('/protected')
    @flask_login.login_required
    def protected():
        page = flask.request.cookies.get('page')
        if page == "map":
            widgets_dict = {
                "player_table_widget": flask.Markup(get_player_table_widget()),
                "system_log_widget": flask.Markup(get_status_log_widget()),
                "location_radar_widget": get_map_widget(),
            }
        elif page == "settings":
            widgets_dict = {
                "settings_general_widget": flask.Markup(get_settings_general_widget()),
                "settings_scheduler_widget": flask.Markup(get_settings_scheduler_widget()),
                "settings_player_observer_widget": flask.Markup(get_settings_player_observer_widget()),
                "system_log_widget": flask.Markup(get_command_log_widget()),
                "system_health_widget": flask.Markup(get_system_health_widget()),
                "location_radar_widget": get_map_widget(),
            }
        else:
            widgets_dict = {
                "player_table_widget": flask.Markup(get_player_table_widget()),
                "whitelist_widget": get_whitelist_widget(),
                "banned_players_widget": get_banned_players_widget(),
                "system_log_widget": flask.Markup(get_status_log_widget()),
                "location_radar_widget": get_map_widget(),
            }

        response = flask.make_response(flask.render_template(
            'index.html',
            title="{} {} - webinterface".format(chrani_bot.dom['bot_name'], chrani_bot.dom['bot_version']),
            webmap_ip=chrani_bot.settings.get_setting_by_name(name="webmap_ip", default="195.201.59.180"),
            webmap_port=chrani_bot.settings.get_setting_by_name(name="webmap_port", default="26953"),
            system_status=get_system_status(),
            chrani_bot=chrani_bot,
            widgets=widgets_dict
        ))
        return response


    @socketio.on('initiate_leaflet', namespace='/chrani-bot/public')
    def init_leaflet(message):
        location_objects = chrani_bot.locations.find_by_distance((0,0,0), 10000)
        location_list = []
        for location_object in location_objects:
            location_list.append(location_object.get_leaflet_marker_json())

        player_objects = chrani_bot.players.get_all_players()
        player_list = []
        for play_object in player_objects:
            player_list.append(play_object.get_leaflet_marker_json())

        # location_objects = chrani_bot.landclaims.get_all_landclaims()
        # lcb_list = []
        # for location_object in location_objects:
        lcb_list = chrani_bot.get_lcb_marker_json(chrani_bot.dom["game_data"]["landclaim_data"])
        socketio.emit('update_leaflet_markers', player_list + location_list + lcb_list, namespace='/chrani-bot/public')


    """ collecting all defined webinterface-actions and creating routes for them """
    for actions_list_entry in actions_list:
        if actions_list_entry['authenticated'] is True:
            action = actions_list_entry['action']
            wrapped_action = flask_login.login_required(action)
            app.add_url_rule(actions_list_entry['route'], view_func=wrapped_action, methods=['GET', 'POST'])
        else:
            action = actions_list_entry['action']
            app.add_url_rule(actions_list_entry['route'], view_func=action, methods=['GET', 'POST'])

    socketio.run(
        app,
        host=chrani_bot.settings.get_setting_by_name(name='bot_ip', default="0.0.0.0"),
        port=chrani_bot.settings.get_setting_by_name(name='bot_port', default="26955"),
        debug=False
    )
