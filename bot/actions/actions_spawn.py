from bot.objects.location import Location
from bot.modules.logger import logger
import common


def on_player_join(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, 'spawn')
    except KeyError:
        location_name = 'Place of Birth'
        location_dict = dict(
            identifier='spawn',
            name=location_name,
            description="{}'s {}".format(target_player.name, location_name),
            owner=target_player.steamid,
            shape='sphere',
            radius=7,
            region=None,
            show_messages=False
        )
        location_object = Location(**location_dict)
        location_object.set_coordinates(target_player)
        try:
            bot.locations.upsert(location_object, save=True)
        except:
            return False

        bot.socketio.emit('update_player_table_row', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
        logger.debug("spawn for player {} created".format(target_player.name))

    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "entered the stream",
        "usage": None
    },
    "action": on_player_join,
    "env": "(self)",
    "group": "spawn",
    "essential": True
})


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "Died",
        "usage": None
    },
    "action": on_player_join,
    "env": "(self)",
    "group": "spawn",
    "essential": True
})


def on_player_death(bot, source_player, target_player, command):
    try:
        location = bot.locations.get(target_player.steamid, 'spawn')
        if target_player.authenticated is False:
            location.enabled = False
            logger.debug("spawn for player {} removed, a new one will be created".format(target_player.name))
    except KeyError:
        return

    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "died",
        "usage": None
    },
    "action": on_player_death,
    "env": "(self)",
    "group": "spawn",
    "essential": True
})
