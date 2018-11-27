import common
import bot.modules.actions
import __main__  # my ide throws a warning here, but it works oO


@common.build_response
def remove_player_from_group(target_player_steamid, group):
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.players.get_by_steamid(target_player_steamid)
    return bot.modules.actions.common.trigger_action(webinterface, player_object, target_player, "remove player {} from group {}".format(target_player_steamid, group))


common.actions_list.append({
    "title": "remove player from group",
    "route": "/protected/authentication/remove/group/<target_player_steamid>/<group>",
    "action": remove_player_from_group,
    "authenticated": True
})


@common.build_response
def add_player_to_group(target_player_steamid, group):
    webinterface = __main__.chrani_bot
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.players.get_by_steamid(target_player_steamid)
    return bot.modules.actions.common.trigger_action(webinterface, player_object, target_player, "add player {} to group {}".format(target_player_steamid, group))


common.actions_list.append({
    "title": "add player to group",
    "route": "/protected/authentication/add/group/<target_player_steamid>/<group>",
    "action": add_player_to_group,
    "authenticated": True
})
