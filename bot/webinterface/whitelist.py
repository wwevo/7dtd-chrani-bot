from flask import request
import common
import bot.modules.player_observer.actions
import __main__  # my ide throws a warning here, but it works oO


def get_whitelist_widget():
    chrani_bot = __main__.chrani_bot
    players_not_on_whitelist_list = [x for x in chrani_bot.players.players_dict.values() if not chrani_bot.whitelist.player_is_on_whitelist(x.steamid)]
    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('/static/widgets/whitelist_general_widget/whitelist_general_widget.html', bot=chrani_bot, players_not_on_whitelist_list=players_not_on_whitelist_list))


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
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "activate whitelist")


common.actions_list.append({
    "title": "activate whitelist",
    "route": "/protected/whitelist/activate",
    "action": activate_whitelist,
    "authenticated": False
})


@common.build_response
def deactivate_whitelist():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "deactivate whitelist")


common.actions_list.append({
    "title": "deactivate whitelist",
    "route": "/protected/whitelist/deactivate",
    "action": deactivate_whitelist,
    "authenticated": False
})


@common.build_response
def remove_player_from_whitelist(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "remove player {} from whitelist".format(target_player_steamid))


common.actions_list.append({
    "title": "remove player from whitelist",
    "route": "/protected/whitelist/remove/player/<string:target_player_steamid>",
    "action": remove_player_from_whitelist,
    "authenticated": True
})


@common.build_response
def add_player_to_whitelist(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    try:
        target_player = chrani_bot.players.get_by_steamid(target_player_steamid)
    except KeyError:
        target_player = None

    form_player_to_add = request.form.get('player_to_add')
    if form_player_to_add:
        target_player_steamid = form_player_to_add

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "add player {} to whitelist".format(target_player_steamid))


common.actions_list.append({
    "title": "add player to whitelist",
    "route": "/protected/whitelist/add/player/<string:target_player_steamid>",
    "action": add_player_to_whitelist,
    "authenticated": True
})
