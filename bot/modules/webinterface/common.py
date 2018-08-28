import os
import __main__  # my ide throws a warning here, but it works oO
from functools import wraps
from urllib import urlencode


def build_response(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        webinterface = __main__.chrani_bot

        action_response = f(*args, **kwargs)
        if action_response:
            response = {
                "actionResponse": action_response.get_message_dict(),
                "actionResult": True
            }
        else:
            response = {
                "actionResponse": {},
                "actionResult": False
            }

        if webinterface.flask.request.accept_mimetypes.best in ['application/json', 'text/javascript']:
            return webinterface.app.response_class(
                response=webinterface.flask.json.dumps(response),
                mimetype='application/json'
            )
        else:
            return webinterface.flask.redirect("/protected?{}".format(urlencode(response)))

    return wrapped


actions_list = []

for module in os.listdir(os.path.dirname(__file__)):
    if module in ['common.py', '__init__.py', 'webinterface.py'] or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module
