import common
import bot.modules.player_observer.actions
import __main__  # my ide throws a warning here, but it works oO


def get_settings_general_widget():
    chrani_bot = __main__.chrani_bot

    output = ""
    settings_dict = chrani_bot.settings.settings_dict
    for setting_name in settings_dict.keys():
        output += get_settings_general_table_row(setting_name)

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/settings_general_widget/settings_general_widget.html', general_entries=output))


common.actions_list.append({
    "title": "get settings general widget",
    "route": "/protected/system/widgets/get_settings_general_widget",
    "action": get_settings_general_widget,
    "authenticated": True
})


def get_settings_general_table_row(setting_name):
    chrani_bot = __main__.chrani_bot

    settings_dict = chrani_bot.settings.settings_dict
    setting_value = settings_dict[setting_name]

    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/settings_general_widget/settings_general_entry.html',
        general_name=setting_name,
        general_value=setting_value,
    ))

    return output


common.actions_list.append({
    "title": "fetches settings general table row",
    "route": "/protected/system/get_settings_general_widget/<string:name>",
    "action": get_settings_general_table_row,
    "authenticated": True
})


def get_settings_scheduler_widget():
    chrani_bot = __main__.chrani_bot

    output = ""
    schedulers_dict = chrani_bot.schedulers_dict
    for name, scheduler in schedulers_dict.iteritems():
        output += get_settings_scheduler_table_row(name)

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/settings_scheduler_widget/settings_scheduler_widget.html', scheduler_entries=output))


common.actions_list.append({
    "title": "get settings scheduler widget",
    "route": "/protected/system/widgets/get_settings_scheduler_widget",
    "action": get_settings_scheduler_widget,
    "authenticated": True
})


def get_settings_scheduler_table_row(name):
    chrani_bot = __main__.chrani_bot

    scheduler_title = chrani_bot.schedulers_dict[name]['title']
    scheduler_status_widget = get_scheduler_status_widget(name)
    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/settings_scheduler_widget/settings_scheduler_entry.html',
        scheduler_name=name,
        scheduler_title=scheduler_title,
        scheduler_status_widget=scheduler_status_widget
    ))

    return output


common.actions_list.append({
    "title": "fetches settings scheduler table row",
    "route": "/protected/system/get_settings_scheduler_widget/<string:name>",
    "action": get_settings_scheduler_table_row,
    "authenticated": True
})


def get_scheduler_status_widget(name):
    chrani_bot = __main__.chrani_bot

    schedulers_controller_status = chrani_bot.schedulers_controller[name]['is_active']

    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/settings_scheduler_widget/scheduler_status.html',
        scheduler_name=name,
        schedulers_controller_status=schedulers_controller_status
    ))
    return output


common.actions_list.append({
    "title": "fetches player status widget",
    "route": "/protected/system/widgets/get_scheduler_status_widget/<string:name>",
    "action": get_scheduler_status_widget,
    "authenticated": True
})


@common.build_response
def disable_scheduler(name):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, None, "disable scheduler {}".format(name))


common.actions_list.append({
    "title": "disable scheduler",
    "route": "/protected/system/settings/disable/scheduler/<string:name>",
    "action": disable_scheduler,
    "authenticated": True
})


@common.build_response
def enable_scheduler(name):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, None, "enable scheduler {}".format(name))


common.actions_list.append({
    "title": "enable scheduler",
    "route": "/protected/system/settings/enable/scheduler/<string:name>",
    "action": enable_scheduler,
    "authenticated": True
})


def get_settings_player_observer_widget():
    chrani_bot = __main__.chrani_bot

    output = ""
    player_observers_dict = chrani_bot.observers_dict
    for name, player_observer in player_observers_dict.iteritems():
        output += get_settings_player_observer_table_row(name)

    return chrani_bot.flask.Markup(chrani_bot.flask.render_template('static/widgets/settings_player_observer_widget/settings_player_observer_widget.html', player_observer_entries=output))


common.actions_list.append({
    "title": "get settings player_observer widget",
    "route": "/protected/system/widgets/get_settings_player_observer_widget",
    "action": get_settings_player_observer_widget,
    "authenticated": True
})


def get_settings_player_observer_table_row(name):
    chrani_bot = __main__.chrani_bot

    player_observer_title = chrani_bot.observers_dict[name]['title']
    player_observer_status_widget = get_player_observer_status_widget(name)
    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/settings_player_observer_widget/settings_player_observer_entry.html',
        player_observer_name=name,
        player_observer_title=player_observer_title,
        player_observer_status_widget=player_observer_status_widget
    ))

    return output


common.actions_list.append({
    "title": "fetches settings player_observer table row",
    "route": "/protected/system/get_settings_player_observer_widget/<string:name>",
    "action": get_settings_player_observer_table_row,
    "authenticated": True
})


def get_player_observer_status_widget(name):
    chrani_bot = __main__.chrani_bot

    player_observers_controller_status = chrani_bot.observers_controller[name]['is_active']

    output = chrani_bot.flask.Markup(chrani_bot.flask.render_template(
        'static/widgets/settings_player_observer_widget/player_observer_status.html',
        player_observer_name=name,
        player_observers_controller_status=player_observers_controller_status
    ))
    return output


common.actions_list.append({
    "title": "fetches player status widget",
    "route": "/protected/system/widgets/get_player_observer_status_widget/<string:name>",
    "action": get_player_observer_status_widget,
    "authenticated": True
})


@common.build_response
def disable_player_observer(name):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)
    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, None, "disable player_observer {}".format(name))


common.actions_list.append({
    "title": "disable player_observer",
    "route": "/protected/system/settings/disable/player_observer/<string:name>",
    "action": disable_player_observer,
    "authenticated": True
})


@common.build_response
def enable_player_observer(name):
    chrani_bot = __main__.chrani_bot
    try:
        source_player_steamid = chrani_bot.flask_login.current_user.steamid
    except AttributeError:
        return chrani_bot.flask.redirect("/")

    player_object = chrani_bot.players.get_by_steamid(source_player_steamid)

    return chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, None, "enable player_observer {}".format(name))


common.actions_list.append({
    "title": "enable player_observer",
    "route": "/protected/system/settings/enable/player_observer/<string:name>",
    "action": enable_player_observer,
    "authenticated": True
})
