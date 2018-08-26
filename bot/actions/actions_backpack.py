from bot.objects.location import Location
import common


def on_player_death(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, 'death')
    except KeyError:
        location_dict = dict(
            identifier='death',
            name='Place of Death',
            owner=target_player.steamid,
            shape='point',
            radius=None,
            region=None
        )
        location_object = Location(**location_dict)

    location_object.set_coordinates(target_player)
    try:
        bot.locations.upsert(location_object, save=True)
    except:
        return False

    target_player.initialized = False
    bot.players.upsert(target_player, save=True)
    bot.tn.send_message_to_player(target_player, "your place of death has been recorded ^^", color=bot.chat_colors['background'])

    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "died",
        "usage": None
    },
    "action": on_player_death,
    "env": "(self)",
    "group": "backpack",
    "essential": False
})


def on_player_kill(bot, source_player, target_player, command):
    return on_player_death(bot, source_player, target_player, command)


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "killed by",
        "usage": None
    },
    "action": on_player_kill,
    "env": "(self)",
    "group": "backpack",
    "essential": False
})


def take_me_to_my_backpack(bot, source_player, target_player, command):
    """Teleports a player to their place of death

    Keyword arguments:
    self -- the bot

    expected bot command:
    /take me to my pack

    example:
    /take me to my pack

    notes:
    a place of death must exist
    will not port if already near the pack
    the place of death will be removed after a successful teleport
    """
    try:
        location_object = bot.locations.get(target_player.steamid, "death")
        if location_object.player_is_inside_boundary(target_player):
            bot.tn.send_message_to_player(target_player, "eh, you already ARE near your pack oO".format(target_player.name), color=bot.chat_colors['warning'])
        else:
            coord_tuple = (location_object.pos_x, -1, location_object.pos_z)
            bot.tn.teleportplayer(target_player, coord_tuple=coord_tuple)
            bot.tn.say("{} can't live without their stuff".format(target_player.name), color=bot.chat_colors['background'])

        bot.locations.remove(target_player.steamid, 'death')

    except KeyError:
        bot.tn.send_message_to_player(target_player, "I don't have your last death on record, sorry :(".format(target_player.name), color=bot.chat_colors['warning'])


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "take me to my pack",
        "usage": "/take me to my pack"
    },
    "action": take_me_to_my_backpack,
    "env": "(self)",
    "group": "backpack",
    "essential": False
})
