from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
import time
import re
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
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "totallyasecret"
        login = LoginManager(app)

        @login.user_loader
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
            return redirect(auth_url)

        @app.route("/logout")
        @login_required
        def logout():
            logout_user()
            return redirect("/")

        @app.route('/authenticate', methods=['GET'])
        def setup():
            valid = validate(request.args)
            if valid is True:
                p = re.search(r"/(?P<steamid>([0-9]{17}))", str(request.args["openid.claimed_id"]))
                if p:
                    steamid = p.group("steamid")
                    try:
                        player_object = self.bot.players.get_by_steamid(steamid)
                        login_user(player_object)
                        return redirect(url_for('protected'))
                    except:
                        pass

            return redirect("/")

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

        @app.route('/')
        def hello_world():
            if self.bot.is_paused is True:
                bot_paused_status = "paused"
            else:
                bot_paused_status = "active"

            time_running_seconds = int(time.time() - self.bot.time_launched)
            time_running = datetime.datetime(1,1,1) + datetime.timedelta(seconds=time_running_seconds)

            output = "Welcome to the {}. I have been running for {}. I am currently {}<br />".format(self.bot.name, "{}d, {}h{}m{}s".format(time_running.day-1, time_running.hour, time_running.minute, time_running.second), bot_paused_status)
            output += "I have {} players on record and manage {} locations.<br />".format(len(self.bot.players.all_players_dict), len(self.bot.locations.all_locations_dict))
            return output

        @app.route('/protected')
        @login_required
        def protected():
            if self.bot.is_paused is True:
                bot_paused_status = "paused"
            else:
                bot_paused_status = "active"

            output = "Welcome to the protected area<br />"
            output += '<a href="/protected/system/pause">pause</a>, <a href="/protected/system/resume">resume</a><br />'
            output += 'the bot is currently {}!<br /><br />'.format(bot_paused_status)
            output += '<a href="/logout">logout user</a><br /><br />'
            output += '<a href="/protected/system/shutdown">shutdown bot</a><br /><br />'
            return output

        @app.route('/protected/system/pause')
        def pause_bot():
            self.bot.is_paused = True
            return redirect(url_for('protected'))

        @app.route('/protected/system/resume')
        def resume_bot():
            self.bot.is_paused = False
            return redirect(url_for('protected'))

        @app.route('/protected/system/shutdown')
        def shutdown():
            self.bot.shutdown()
            return redirect(url_for('protected'))

        app.run(host=self.bot.settings.get_setting_by_name('bot_ip'), port=self.bot.settings.get_setting_by_name('bot_port'), debug=False)
