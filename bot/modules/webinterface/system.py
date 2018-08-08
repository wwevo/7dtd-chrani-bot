import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO
from urllib import urlencode


def pause_bot():
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "pause bot")
    response = {
        "actionResponse": "{} has been paused".format(webinterface.bot.name),
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
    "authenticated": True
})


def resume_bot():
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "resume bot")
    response = {
        "actionResponse": "{} has been resumed".format(webinterface.bot.name),
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
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "shut down the matrix")
    response = {
        "actionResponse": "{} has been shut down".format(webinterface.bot.name),
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


