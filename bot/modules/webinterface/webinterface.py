from flask import Flask, redirect, request
import time
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

        @app.route('/login')
        def login():
            steam_openid_url = 'https://steamcommunity.com/openid/login'
            u = {
                'openid.ns': "http://specs.openid.net/auth/2.0",
                'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
                'openid.mode': 'checkid_setup',
                'openid.return_to': 'http://127.0.0.1:5000/authenticate',
                'openid.realm': 'http://127.0.0.1:5000'
            }
            query_string = urlencode(u)
            auth_url = steam_openid_url + "?" + query_string
            return redirect(auth_url)

        @app.route('/authenticate', methods=['GET'])
        def setup():
            valid = validate(request.args)
            if valid is True:
                return redirect("/protected")
            else:
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
            output = "Welcome to the {}. I have been running for {}<br />".format(self.bot.name, time.strftime("%H:%M:%S", time.gmtime(time.time() - self.bot.time_launched)))
            output += "I have {} players on record and manage {} locations.<br />".format(len(self.bot.players.all_players_dict), len(self.bot.locations.all_locations_dict))
            return output

        @app.route('/protected')
        def protected():
            return "Welcome to the protected area"

        app.run()