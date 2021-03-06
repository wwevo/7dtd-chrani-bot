from flask import request
import common
import __main__  # my ide throws a warning here, but it works oO


def get_player_status(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    player_status = {
        "is_online": chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["is_online"],
        "is_logging_in": chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["is_logging_in"]
    }
    return chrani_bot.app.response_class(
        response=chrani_bot.flask.json.dumps(player_status),
        mimetype='application/json'
    )


common.actions_list.append({
    "title": "fetches player status",
    "route": "/protected/players/get_status/<string:target_player_steamid>",
    "action": get_player_status,
    "authenticated": True
})


def get_player_whitelist_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    except KeyError:
        return ""

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/whitelist_status.html', bot=chrani_bot, player_object=player_object))


common.actions_list.append({
    "title": "fetches player whitelist widget",
    "route": "/protected/players/widgets/player_whitelist_widget/<string:target_player_steamid>",
    "action": get_player_whitelist_widget,
    "authenticated": True
})


def get_player_lcb_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    except KeyError:
        return ""

    try:
        lcb_list = chrani_bot.dom["game_data"]["landclaim_data"][target_player_steamid]
    except:
        lcb_list = []

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/lcb.html', bot=chrani_bot, player_object=player_object, lcb_list=lcb_list))


common.actions_list.append({
    "title": "fetches player lcb widget",
    "route": "/protected/players/widgets/player_lcb_widget/<string:target_player_steamid>",
    "action": get_player_lcb_widget,
    "authenticated": True
})


def get_player_permissions_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    player_permissions_dict = player_object.get_permission_levels_dict(chrani_bot.permission_levels_list)
    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/authentication_groups.html', player_object=player_object, player_permissions_dict=player_permissions_dict))


common.actions_list.append({
    "title": "fetches player permissions widget",
    "route": "/protected/players/widgets/player_permissions_widget/<string:target_player_steamid>",
    "action": get_player_permissions_widget,
    "authenticated": True
})


def get_player_actions_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/actions.html', player_object=player_object))


common.actions_list.append({
    "title": "fetches player actions widget",
    "route": "/protected/players/widgets/player_actions_widget/<string:target_player_steamid>",
    "action": get_player_actions_widget,
    "authenticated": True
})


def get_player_status_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    except KeyError:
        return ""

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/status.html', player_object=player_object))


common.actions_list.append({
    "title": "fetches player status widget",
    "route": "/protected/players/widgets/player_status_widget/<string:target_player_steamid>",
    "action": get_player_status_widget,
    "authenticated": True
})


def get_player_locations_widget(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    player_object = chrani_bot.players.get_by_steamid(target_player_steamid)
    try:
        player_locations_dict = chrani_bot.locations.get(target_player_steamid)
    except KeyError:
        return ""

    try:
        public_locations_dict = chrani_bot.locations.get('system')
    except KeyError:
        public_locations_dict = None

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/locations.html', player_object=player_object, player_locations_dict=player_locations_dict, public_locations_dict=public_locations_dict))


common.actions_list.append({
    "title": "fetches player locations widget",
    "route": "/protected/players/widgets/player_locations_widget/<string:target_player_steamid>",
    "action": get_player_locations_widget,
    "authenticated": True
})


def get_all_players_table_row(steamid):
    chrani_bot = __main__.chrani_bot
    player_object = chrani_bot.players.get_by_steamid(steamid)

    player_permissions_widget = get_player_permissions_widget(player_object.steamid)
    player_whitelist_widget = get_player_whitelist_widget(player_object.steamid)
    player_locations_widget = get_player_locations_widget(player_object.steamid)
    player_actions_widget = get_player_actions_widget(player_object.steamid)
    player_lcb_widget = get_player_lcb_widget(player_object.steamid)
    player_status_widget = get_player_status_widget(player_object.steamid)

    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/players_table_widget/player_table_entry.html',
        player_object=player_object,
        player_whitelist_widget=player_whitelist_widget,
        player_locations_widget=player_locations_widget,
        player_lcb_widget=player_lcb_widget,
        player_permissions_widget=player_permissions_widget,
        player_actions_widget=player_actions_widget,
        player_status_widget=player_status_widget
    ))

    return output


common.actions_list.append({
    "title": "fetches player table row",
    "route": "/protected/players/get_player_table_row/<string:steamid>",
    "action": get_all_players_table_row,
    "authenticated": True
})


def get_player_table_widget():
    chrani_bot = __main__.chrani_bot

    output = ""
    player_objects_list = chrani_bot.players.get_all_players()
    player_objects_list = [player_object for player_object in sorted(player_objects_list, key=lambda x: x.last_seen, reverse=True)]
    for player_object in player_objects_list:
        if not player_object.is_to_be_obliterated:
            output += get_all_players_table_row(player_object.steamid)

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/players_table_widget/player_table_widget.html', player_entries=output))


common.actions_list.append({
    "title": "get player table widget",
    "route": "/protected/players/widgets/get_player_table_widget",
    "action": get_player_table_widget,
    "authenticated": True
})


@common.build_response
def send_player_home(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        location_object = chrani_bot.locations.get(target_player_steamid, 'home')
        pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
        coord_tuple = (pos_x, pos_y, pos_z)
    except (KeyError, AttributeError):
        coord_tuple = (None, None, None)

    return send_player_to_coords(target_player_steamid, coord_tuple)


common.actions_list.append({
    "title": "send player home",
    "route": "/protected/players/send/<string:target_player_steamid>/home",
    "action": send_player_home,
    "authenticated": True
})


@common.build_response
def send_player_to_lobby(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    try:
        location_object = chrani_bot.locations.get('system', 'lobby')
        pos_x, pos_y, pos_z = location_object.get_teleport_coordinates()
        coord_tuple = (pos_x, pos_y, pos_z)
    except (KeyError, AttributeError):
        coord_tuple = (None, None, None)

    return send_player_to_coords(target_player_steamid, coord_tuple)


common.actions_list.append({
    "title": "send player to lobby",
    "route": "/protected/players/send/<string:target_player_steamid>/lobby",
    "action": send_player_to_lobby,
    "authenticated": True
})


@common.build_response
def send_player_to_coords(target_player_steamid, coords_tuple_string):
    chrani_bot = __main__.chrani_bot
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)

    try:
        coord_tuple = eval(coords_tuple_string)
        if type(coord_tuple) is not tuple:
            raise AttributeError
    except (KeyError, AttributeError):
        coord_tuple = (None, None, None)

    form_coord_tuple = request.form.get('coords')
    if form_coord_tuple:
        coord_tuple = form_coord_tuple

    val = chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "send player {} to {}".format(target_player_steamid, str(coord_tuple)))
    return val


common.actions_list.append({
    "title": "send player to coords",
    "route": "/protected/players/send/<string:target_player_steamid>/to/<string:coords_tuple_string>",
    "action": send_player_to_coords,
    "authenticated": True
})


@common.build_response
def obliterate_player(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "obliterate player {}".format(target_player_steamid))


common.actions_list.append({
    "title": "obliterate player",
    "route": "/protected/players/obliterate/<string:target_player_steamid>",
    "action": obliterate_player,
    "authenticated": True
})


@common.build_response
def ban_player(target_player_steamid, reason):
    chrani_bot = __main__.chrani_bot
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)
    form_reason = request.form.get('reason')
    if form_reason:
        reason = form_reason

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "ban player {} for {}".format(target_player_steamid, reason))


common.actions_list.append({
    "title": "ban player",
    "route": "/protected/players/ban/<string:target_player_steamid>/<reason>",
    "action": ban_player,
    "authenticated": True
})


@common.build_response
def kick_player(target_player_steamid, reason):
    chrani_bot = __main__.chrani_bot
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)

    form_reason = request.form.get('reason')
    if form_reason:
        reason = form_reason

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "kick player {} for {}".format(target_player_steamid, reason))


common.actions_list.append({
    "title": "kick player",
    "route": "/protected/players/kick/<string:target_player_steamid>/<reason>",
    "action": kick_player,
    "authenticated": True
})


@common.build_response
def unban_player(target_player_steamid):
    chrani_bot = __main__.chrani_bot
    target_player_steamid = str(target_player_steamid)
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    target_player = chrani_bot.players.get_by_steamid(target_player_steamid)

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, target_player, "unban player {}".format(target_player_steamid))


common.actions_list.append({
    "title": "unban player",
    "route": "/protected/players/unban/<string:target_player_steamid>",
    "action": unban_player,
    "authenticated": True
})


