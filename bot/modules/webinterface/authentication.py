import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO
from urllib import urlencode


def remove_player_from_group(steamid, group):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "remove player {} from group {}".format(steamid, group))
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
    "title": "remove player from group",
    "route": "/protected/authentication/remove/group/<steamid>/<group>",
    "action": remove_player_from_group,
    "authenticated": True
})


def add_player_to_group(steamid, group):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "add player {} to group {}".format(steamid, group))
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
    "title": "add player to group",
    "route": "/protected/authentication/add/group/<steamid>/<group>",
    "action": add_player_to_group,
    "authenticated": True
})
