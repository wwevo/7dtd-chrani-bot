import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO
from urllib import urlencode


def send_player_home(steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)
    location_object = webinterface.bot.locations.get(steamid, 'home')
    pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
    coord_tuple = (pos_x, pos_y, pos_z)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "send player {} to {}".format(steamid, str(coord_tuple)))

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
    "title": "send player home",
    "route": "/protected/players/send/<steamid>/home",
    "action": send_player_home,
    "authenticated": True
})


def send_player_to_lobby(steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)

    location_object = webinterface.bot.locations.get('system', 'lobby')
    pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
    coord_tuple = (pos_x, pos_y, pos_z)
    action_response = bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "send player {} to {}".format(steamid, str(coord_tuple)))

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
    "title": "send player home",
    "route": "/protected/players/send/<steamid>/to/lobby",
    "action": send_player_to_lobby,
    "authenticated": True
})


def obliterate_player(steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)
    action_response = webinterface.bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "obliterate player {}".format(steamid))
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
    "title": "obliterate player",
    "route": "/protected/players/obliterate/<steamid>",
    "action": obliterate_player,
    "authenticated": True
})


def kick_player(steamid, reason):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(webinterface.flask_login.current_user.steamid)
    target_player = webinterface.bot.players.get_by_steamid(steamid)
    action_response = webinterface.bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "kick player {} for {}".format(steamid, reason))
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
    "title": "kick player",
    "route": "/protected/players/kick/<steamid>/<reason>",
    "action": kick_player,
    "authenticated": True
})


