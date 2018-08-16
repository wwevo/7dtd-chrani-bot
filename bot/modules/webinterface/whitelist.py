import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO


def get_whitelist_widget():
    webinterface = __main__.chrani_bot
    return webinterface.flask.Markup(webinterface.flask.render_template('whitelist_widget.html', bot=webinterface))


common.actions_list.append({
    "title": "fetches whitelist widget",
    "route": "/protected/players/widgets/whitelist_widget",
    "action": get_whitelist_widget,
    "authenticated": True
})


def get_whitelist_status():
    return get_whitelist_widget()


@common.build_response
def activate_whitelist():
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    return bot.actions.common.trigger_action(webinterface, player_object, player_object, "activate whitelist")


common.actions_list.append({
    "title": "activate whitelist",
    "route": "/protected/whitelist/activate",
    "action": activate_whitelist,
    "authenticated": False
})


@common.build_response
def deactivate_whitelist():
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    return bot.actions.common.trigger_action(webinterface, player_object, player_object, "deactivate whitelist")


common.actions_list.append({
    "title": "deactivate whitelist",
    "route": "/protected/whitelist/deactivate",
    "action": deactivate_whitelist,
    "authenticated": False
})


@common.build_response
def remove_player_from_whitelist(target_player_steamid):
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.players.get_by_steamid(target_player_steamid)
    return bot.actions.common.trigger_action(webinterface, player_object, target_player, "remove player {} from whitelist".format(target_player_steamid))


common.actions_list.append({
    "title": "remove player from whitelist",
    "route": "/protected/whitelist/remove/player/<string:target_player_steamid>",
    "action": remove_player_from_whitelist,
    "authenticated": True
})


@common.build_response
def add_player_to_whitelist(target_player_steamid):
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.players.get_by_steamid(target_player_steamid)
    return bot.actions.common.trigger_action(webinterface, player_object, target_player, "add player {} to whitelist".format(target_player_steamid))


common.actions_list.append({
    "title": "add player to whitelist",
    "route": "/protected/whitelist/add/player/<string:target_player_steamid>",
    "action": add_player_to_whitelist,
    "authenticated": True
})
