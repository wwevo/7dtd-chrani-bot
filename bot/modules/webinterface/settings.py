from flask import request
import common
import bot.actions
import __main__  # my ide throws a warning here, but it works oO


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
    return bot.actions.common.trigger_action(chrani_bot, player_object, None, "disable scheduler {}".format(name))


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

    return bot.actions.common.trigger_action(chrani_bot, player_object, None, "enable scheduler {}".format(name))


common.actions_list.append({
    "title": "enable scheduler",
    "route": "/protected/system/settings/enable/scheduler/<string:name>",
    "action": enable_scheduler,
    "authenticated": True
})
