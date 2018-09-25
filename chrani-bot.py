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
import bot.actions
from bot.modules.webinterface.players import get_player_table_widget
from bot.modules.webinterface.system import get_system_status
from bot.modules.webinterface.whitelist import get_whitelist_widget
from bot.modules.webinterface.players import get_banned_players_widget
from bot.modules.webinterface.locations import get_player_location_radar_widget

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
    chrani_bot_thread = ChraniBot(chrani_bot_thread_stop_flag, app, flask, flask_login, socketio)
    chrani_bot_thread.name = "chrani_bot"  # nice to have for the logs
    chrani_bot_thread.app_root = root_dir
    chrani_bot_thread.bot_version = "0.7.003"
    chrani_bot = chrani_bot_thread

    chrani_bot.start()


    @login_manager.user_loader
    def user_loader(steamid):
        try:
            player_object = chrani_bot.players.get_by_steamid(steamid)
            # authentication_groups = chrani_bot.settings.get_setting_by_name("authentication_groups")
            if any(x in ["donator", "mod", "admin"] for x in player_object.permission_levels):
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
            'openid.return_to': "http://{}:{}/authenticate".format(chrani_bot.settings.get_setting_by_name('bot_ip'), chrani_bot.settings.get_setting_by_name('bot_port')),
            'openid.realm': "http://{}:{}".format(chrani_bot.settings.get_setting_by_name('bot_ip'), chrani_bot.settings.get_setting_by_name('bot_port'))
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
                    flask_login.login_user(player_object, remember=True)
                    return flask.redirect("/protected")
                except:
                    pass

        return flask.redirect("/")


    @app.route('/unauthorized')
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        output = 'You are not authorized. You need to be authenticated in-game to get access to the webinterface ^^<br />'
        output += '<a href="/">home</a><br /><br />'
        markup = flask.Markup(output)
        return flask.render_template('index.html', bot=chrani_bot, content=markup)


    @app.errorhandler(404)
    def page_not_found(error):
        output = 'Page not found :(<br />'
        output += '<a href="/">home</a><br /><br />'
        markup = flask.Markup(output)
        return flask.render_template('index.html', bot=chrani_bot, content=markup), 404


    @app.route('/')
    def index():
        if flask_login.current_user.is_authenticated is True:
            return flask.redirect("/protected")

        output = "Welcome to the <strong>{}</strong><br />".format(chrani_bot.name)

        markup = flask.Markup(output)
        system_status_widget = get_system_status()
        return flask.render_template('index.html', bot=chrani_bot, content=markup, system_status_widget=system_status_widget)


    @app.route('/protected')
    @flask_login.login_required
    def protected():
        widgets_dict = {
            "player_table_widget": flask.Markup(get_player_table_widget()),
            "whitelist_widget": get_whitelist_widget(),
            "banned_players_widget": get_banned_players_widget(),
            "command_log_widget": flask.Markup(flask.render_template('command_log_widget.html')),
            "location_radar_widget": get_player_location_radar_widget(),
        }

        return flask.render_template(
            'index.html',
            system_status=get_system_status(),
            bot=chrani_bot,
            widgets=widgets_dict
        )


    @socketio.on('initiate_leaflet', namespace='/chrani-bot/public')
    def init_leaflet(message):
        location_objects = chrani_bot.locations.find_by_distance((0,0,0), 10000)
        location_list = chrani_bot.locations.get_leaflet_marker_json(location_objects)
        player_objects = chrani_bot.players.get_all_players()
        player_list = chrani_bot.players.get_leaflet_marker_json(player_objects)
        lcb_list = chrani_bot.get_lcb_marker_json(chrani_bot.landclaims_dict)
        socketio.emit('update_leaflet_markers', player_list + location_list + lcb_list, namespace='/chrani-bot/public')


    """ collecting all defined webinterface-actions and creating routes for them """
    for actions_list_entry in bot.modules.webinterface.actions_list:
        if actions_list_entry['authenticated'] is True:
            action = actions_list_entry['action']
            wrapped_action = flask_login.login_required(action)
            app.add_url_rule(actions_list_entry['route'], view_func=wrapped_action, methods=['GET', 'POST'])
        else:
            action = actions_list_entry['action']
            app.add_url_rule(actions_list_entry['route'], view_func=action, methods=['GET', 'POST'])

    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
