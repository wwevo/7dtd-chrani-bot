from urllib import urlencode
import flask
import flask_login
import re
from threading import *


class RestfulApi(Thread):
    bot = object
    app = object

    def __init__(self, event, bot):
        self.bot = bot
        self.stopped = event
        Thread.__init__(self)

    def run(self):
        steam_openid_url = 'https://steamcommunity.com/openid/login'
        app = flask.Flask(self.bot.bot_name + " webservice")
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
            return '<a href="http://' + bot_ip + ':' + str(bot_port) + '/login">Login with steam</a>'

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

                    print "^^" + player_object.name + "^^"
                    print "^^" + str(status) + "^^"
                    return flask.redirect(flask.url_for('protected'))
                except:
                    pass

            return flask.redirect('/unauthorized')

        @app.route('/protected')
        @flask_login.login_required
        def protected():
            if flask_login.current_user.steamid in self.bot.active_player_threads_dict:
                status = "in game"
            else:
                status = "not in game"
            output = 'Logged in as: ' + str(flask_login.current_user.name) + ", currently " + status + "<br />"
            output += '<a href="http://' + bot_ip + ':' + str(bot_port) + '/logout">logout</a>'
            return output

        @app.route('/logout')
        def logout():
            flask_login.logout_user()
            return flask.redirect('/')

        @app.route('/unauthorized')
        @login_manager.unauthorized_handler
        def unauthorized_handler():
            output = 'You are not authorized. You need to be authenticated in-game to get access to the webinterface ^^'
            return output

        app.run(host=bot_ip)
