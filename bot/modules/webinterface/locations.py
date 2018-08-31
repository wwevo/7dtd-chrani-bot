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


def get_player_locations():
    bot = __main__.chrani_bot
    locations_objects = bot.locations.find_by_distance((0,0,0), 10000)
    location_list = []
    for location in locations_objects:
        location_list.append({
            "owner": location.values()[0].owner,
            "identifier": location.values()[0].identifier,
            "radius": location.values()[0].radius,
            "pos_x": location.values()[0].pos_x,
            "pos_y": location.values()[0].pos_y,
            "pos_z": location.values()[0].pos_z
        })

    return bot.app.response_class(
        response=bot.flask.json.dumps(location_list),
        mimetype='application/json'
    )


common.actions_list.append({
    "title": "fetches player locations",
    "route": "/protected/players/player_locations",
    "action": get_player_locations,
    "authenticated": True
})


