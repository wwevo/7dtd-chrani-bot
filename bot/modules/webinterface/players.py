import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO


def get_player_whitelist_widget(target_player_steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(target_player_steamid)
    return webinterface.flask.Markup(webinterface.flask.render_template('player_whitelist_widget.html', bot=webinterface.bot, player_object=player_object))


common.actions_list.append({
    "title": "fetches player whitelist widget",
    "route": "/protected/players/widgets/player_whitelist_widget/<string:target_player_steamid>",
    "action": get_player_whitelist_widget,
    "authenticated": True
})


def get_player_permissions_widget(target_player_steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(target_player_steamid)
    player_permissions_dict = player_object.get_permission_levels_dict(webinterface.bot.permission_levels_list)
    return webinterface.flask.Markup(webinterface.flask.render_template('player_permissions_widget.html', player_object=player_object, player_permissions_dict=player_permissions_dict))


common.actions_list.append({
    "title": "fetches player permissions widget",
    "route": "/protected/players/widgets/player_permissions_widget/<string:target_player_steamid>",
    "action": get_player_permissions_widget,
    "authenticated": True
})


def get_obliterate_player_widget(target_player_steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(target_player_steamid)
    return webinterface.flask.Markup(webinterface.flask.render_template('obliterate_player_widget.html', player_object=player_object))


common.actions_list.append({
    "title": "fetches obliterate player widget",
    "route": "/protected/players/widgets/obliterate_player_widget/<string:target_player_steamid>",
    "action": get_obliterate_player_widget,
    "authenticated": True
})


def get_player_locations_widget(target_player_steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(target_player_steamid)
    player_locations_dict = webinterface.bot.locations.get(target_player_steamid)
    return webinterface.flask.Markup(webinterface.flask.render_template('player_locations_widget.html', player_object=player_object, player_locations_dict=player_locations_dict))


common.actions_list.append({
    "title": "fetches player locations widget",
    "route": "/protected/players/widgets/player_locations_widget/<string:target_player_steamid>",
    "action": get_player_locations_widget,
    "authenticated": True
})


def get_online_players_table():
    webinterface = __main__.bot.webinterface
    player_objects_to_list = webinterface.bot.players.get_all_players(get_online_only=True)

    return webinterface.flask.render_template('online_players.html', player_objects_to_list=player_objects_to_list)


def get_all_players_table_row(steamid):
    webinterface = __main__.bot.webinterface
    player_object = webinterface.bot.players.get_by_steamid(steamid)

    player_permissions_widget = get_player_permissions_widget(player_object.steamid)
    player_whitelist_widget = get_player_whitelist_widget(player_object.steamid)
    player_locations_widget = get_player_locations_widget(player_object.steamid)
    obliterate_player_widget = get_obliterate_player_widget(player_object.steamid)

    output = webinterface.flask.Markup(webinterface.flask.render_template(
        'all_players_entry.html',
        player_object=player_object,
        player_whitelist_widget=player_whitelist_widget,
        player_locations_widget=player_locations_widget,
        player_permissions_widget=player_permissions_widget,
        obliterate_player_widget=obliterate_player_widget
    ))

    return output


common.actions_list.append({
    "title": "fetches players table_row",
    "route": "/protected/players/get_table_row/<string:steamid>",
    "action": get_all_players_table_row,
    "authenticated": True
})


def get_all_players_table():
    webinterface = __main__.bot.webinterface

    output = ""
    player_objects_list = webinterface.bot.players.get_all_players()
    player_objects_list = sorted(player_objects_list, key=lambda x: (x.is_online, x.authenticated), reverse=True)
    for player_object in player_objects_list:
        output += get_all_players_table_row(player_object.steamid)

    return webinterface.flask.render_template('all_players.html', player_entries=output)


def get_players_table(online_only=False):
    if online_only:
        return get_online_players_table()
    else:
        return get_all_players_table()


@common.build_response
def send_player_home(target_player_steamid):
    webinterface = __main__.bot.webinterface
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.bot.players.get_by_steamid(target_player_steamid)
    try:
        location_object = webinterface.bot.locations.get(target_player_steamid, 'home')
        pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
        coord_tuple = (pos_x, pos_y, pos_z)
    except KeyError:
        return False

    return bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "send player {} to {}".format(target_player_steamid, str(coord_tuple)))


common.actions_list.append({
    "title": "send player home",
    "route": "/protected/players/send/<string:target_player_steamid>/home",
    "action": send_player_home,
    "authenticated": True
})


@common.build_response
def send_player_to_lobby(target_player_steamid):
    webinterface = __main__.bot.webinterface
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.bot.players.get_by_steamid(target_player_steamid)

    location_object = webinterface.bot.locations.get('system', 'lobby')
    pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
    coord_tuple = (pos_x, pos_y, pos_z)

    return bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "send player {} to {}".format(target_player_steamid, str(coord_tuple)))


common.actions_list.append({
    "title": "send player home",
    "route": "/protected/players/send/<string:target_player_steamid>/to/lobby",
    "action": send_player_to_lobby,
    "authenticated": True
})


@common.build_response
def obliterate_player(target_player_steamid):
    webinterface = __main__.bot.webinterface
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.bot.players.get_by_steamid(target_player_steamid)

    return bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "obliterate player {}".format(target_player_steamid))


common.actions_list.append({
    "title": "obliterate player",
    "route": "/protected/players/obliterate/<string:target_player_steamid>",
    "action": obliterate_player,
    "authenticated": True
})


@common.build_response
def kick_player(target_player_steamid, reason):
    webinterface = __main__.bot.webinterface
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = webinterface.flask_login.current_user.steamid
    except AttributeError:
        return webinterface.flask.redirect("/")

    player_object = webinterface.bot.players.get_by_steamid(source_player_steamid)
    target_player = webinterface.bot.players.get_by_steamid(target_player_steamid)

    return bot.actions.common.trigger_action(webinterface.bot, player_object, target_player, "kick player {} for {}".format(target_player_steamid, reason))


common.actions_list.append({
    "title": "kick player",
    "route": "/protected/players/kick/<string:target_player_steamid>/<reason>",
    "action": kick_player,
    "authenticated": True
})


