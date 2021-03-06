import common
import __main__  # my ide throws a warning here, but it works oO


def get_system_health_widget():
    chrani_bot = __main__.chrani_bot

    result = chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/system_health_widget/system_health_widget.html', health_dict=chrani_bot.custodian.health_dict, bot=chrani_bot))
    chrani_bot.custodian.clear_status()

    return result


common.actions_list.append({
    "title": "fetches system health widget",
    "route": "/protected/players/widgets/system_health_widget",
    "action": get_system_health_widget,
    "authenticated": True
})


def get_banned_players_widget():
    webinterface = __main__.chrani_bot

    return webinterface.flask.Markup(webinterface.flask.render_template('static/widgets/system_banned_players_widget/system_banned_players_widget.html', bot=webinterface))


common.actions_list.append({
    "title": "fetches banned players widget",
    "route": "/protected/system/widgets/system_banned_players_widget",
    "action": get_banned_players_widget,
    "authenticated": True
})


def get_status_log_widget():
    bot = __main__.chrani_bot
    return bot.flask.Markup(bot.flask.render_template('static/widgets/system_log_widget/system_log_widget.html', widget_id="status_log", widget_title="status log", bot=bot))


common.actions_list.append({
    "title": "fetches map widget",
    "route": "/protected/system/widgets/status_log_widget",
    "action": get_status_log_widget,
    "authenticated": True
})


def get_command_log_widget():
    bot = __main__.chrani_bot
    return bot.flask.Markup(bot.flask.render_template('static/widgets/system_log_widget/system_log_widget.html', widget_id="command_log", widget_title="command log", bot=bot))


common.actions_list.append({
    "title": "fetches map widget",
    "route": "/protected/system/widgets/command_log_widget",
    "action": get_command_log_widget,
    "authenticated": True
})


def get_map_widget():
    bot = __main__.chrani_bot
    return bot.flask.Markup(bot.flask.render_template('static/widgets/system_map_widget/system_map_widget.html', bot=bot))


common.actions_list.append({
    "title": "fetches map widget",
    "route": "/protected/system/widgets/map_widget",
    "action": get_map_widget,
    "authenticated": True
})


def get_system_status_widget():
    chrani_bot = __main__.chrani_bot
    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/system_status_widget/system_status_widget.html', bot=chrani_bot))


common.actions_list.append({
    "title": "fetches system status widget",
    "route": "/protected/players/widgets/system_status_widget",
    "action": get_system_status_widget,
    "authenticated": False
})


def get_system_status():
    return get_system_status_widget()


@common.build_response
def pause_bot():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "pause bot")


common.actions_list.append({
    "title": "pause bot",
    "route": "/protected/system/pause",
    "action": pause_bot,
    "authenticated": False
})


@common.build_response
def resume_bot():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "resume bot")


common.actions_list.append({
    "title": "resume bot",
    "route": "/protected/system/resume",
    "action": resume_bot,
    "authenticated": True
})


@common.build_response
def shutdown():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "shut down the matrix")


common.actions_list.append({
    "title": "shut down",
    "route": "/protected/system/shutdown",
    "action": shutdown,
    "authenticated": True
})


@common.build_response
def reinitialize():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "reinitialize")


common.actions_list.append({
    "title": "reinitialize",
    "route": "/protected/system/reinitialize",
    "action": reinitialize,
    "authenticated": True
})


@common.build_response
def shutdown_server():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "shut down the world")


common.actions_list.append({
    "title": "shutdown server",
    "route": "/protected/system/shutdown/server",
    "action": shutdown_server,
    "authenticated": True
})


@common.build_response
def skip_bloodmoon():
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "skip bloodmoon")


common.actions_list.append({
    "title": "skip bloodmoon",
    "route": "/protected/system/skip_bloodmoon",
    "action": skip_bloodmoon,
    "authenticated": True
})


