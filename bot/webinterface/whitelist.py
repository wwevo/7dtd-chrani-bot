from flask import request
import common
import bot.modules.actions
import __main__  # my ide throws a warning here, but it works oO


def get_whitelist_widget():
    webinterface = __main__.chrani_bot
    players_not_on_whitelist_list = [x for x in webinterface.players.players_dict.values() if not webinterface.whitelist.player_is_on_whitelist(x.steamid)]
    return webinterface.flask.Markup(webinterface.flask.render_template('/static/widgets/whitelist_general_widget/whitelist_general_widget.html', bot=webinterface, players_not_on_whitelist_list=players_not_on_whitelist_list))


common.actions_list.append({
    "title": "fetches whitelist widget",
    "route": "/protected/system/widgets/whitelist_general_widget",
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
    return bot.modules.actions.common.trigger_action(webinterface, player_object, player_object, "activate whitelist")


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
    return bot.modules.actions.common.trigger_action(webinterface, player_object, player_object, "deactivate whitelist")


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
    return bot.modules.actions.common.trigger_action(webinterface, player_object, target_player, "remove player {} from whitelist".format(target_player_steamid))


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
    try:
        target_player = webinterface.players.get_by_steamid(target_player_steamid)
    except KeyError:
        target_player = None

    form_player_to_add = request.form.get('player_to_add')
    if form_player_to_add:
        target_player_steamid = form_player_to_add

    return bot.modules.actions.common.trigger_action(webinterface, player_object, target_player, "add player {} to whitelist".format(target_player_steamid))


common.actions_list.append({
    "title": "add player to whitelist",
    "route": "/protected/whitelist/add/player/<string:target_player_steamid>",
    "action": add_player_to_whitelist,
    "authenticated": True
})
