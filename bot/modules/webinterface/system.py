import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO


def get_system_status_widget():
    webinterface = __main__.bot.webinterface
    return webinterface.flask.Markup(webinterface.flask.render_template('system_status_widget.html', bot=webinterface.bot))


common.actions_list.append({
    "title": "fetches system status widget",
    "route": "/protected/players/widgets/system_status_widget",
    "action": get_system_status_widget,
    "authenticated": True
})


def get_system_status():
    return get_system_status_widget()

@common.build_response
def pause_bot():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)

    return bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "pause bot")


common.actions_list.append({
    "title": "pause bot",
    "route": "/protected/system/pause",
    "action": pause_bot,
    "authenticated": False
})


@common.build_response
def resume_bot():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)

    return bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "resume bot")


common.actions_list.append({
    "title": "resume bot",
    "route": "/protected/system/resume",
    "action": resume_bot,
    "authenticated": True
})


@common.build_response
def shutdown():
    webinterface = __main__.bot.webinterface
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    return bot.actions.common.trigger_action(webinterface.bot, player_object, player_object, "shut down the matrix")


common.actions_list.append({
    "title": "shut down",
    "route": "/protected/system/shutdown",
    "action": shutdown,
    "authenticated": True
})


