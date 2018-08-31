import common
import __main__  # my ide throws a warning here, but it works oO


def get_player_location_radar_widget():
    bot = __main__.chrani_bot

    return bot.flask.Markup(bot.flask.render_template('player_location_radar_widget.html', bot=bot))


common.actions_list.append({
    "title": "fetches player location radar widget",
    "route": "/protected/players/widgets/player_locations_radar_widget",
    "action": get_player_location_radar_widget,
    "authenticated": True
})


