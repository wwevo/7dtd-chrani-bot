import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO
from urllib import urlencode


def pause_bot():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "pause bot")
    response = {
        "actionResponse": action_response,
        "actionResult": True
    }

    if webinterface.flask.request.accept_mimetypes.best == 'application/json':
        return webinterface.app.response_class(
            response=webinterface.flask.json.dumps(response),
            mimetype='application/json'
        )
    else:
        return webinterface.flask.redirect("/protected?{}".format(urlencode(response)))


common.actions_list.append({
    "title": "pause bot",
    "route": "/protected/system/pause",
    "action": pause_bot,
    "authenticated": False
})


def resume_bot():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "resume bot")
    response = {
        "actionResponse": action_response,
        "actionResult": True
    }
    if webinterface.flask.request.accept_mimetypes.best == 'application/json':
        return webinterface.app.response_class(
            response=webinterface.flask.json.dumps(response),
            mimetype='application/json'
        )
    else:
        return webinterface.flask.redirect("/protected?{}".format(urlencode(response)))


common.actions_list.append({
    "title": "resume bot",
    "route": "/protected/system/resume",
    "action": resume_bot,
    "authenticated": True
})


def shutdown():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "shut down the matrix")
    response = {
        "actionResponse": action_response,
        "actionResult": True
    }
    if webinterface.flask.request.accept_mimetypes.best == 'application/json':
        return webinterface.app.response_class(
            response=webinterface.flask.json.dumps(response),
            mimetype='application/json'
        )
    else:
        return webinterface.flask.redirect("/protected?{}".format(urlencode(response)))


common.actions_list.append({
    "title": "shut down",
    "route": "/protected/system/shutdown",
    "action": shutdown,
    "authenticated": True
})


