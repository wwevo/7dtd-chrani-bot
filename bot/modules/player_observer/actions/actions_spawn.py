from bot.objects.location import Location
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def on_player_join(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            location_object = chrani_bot.locations.get(target_player.steamid, 'spawn')
        except KeyError:
            location_name = 'Place of Birth'
            location_dict = dict(
                identifier='spawn',
                name=location_name,
                description="{}'s {}".format(target_player.name, location_name),
                owner=target_player.steamid,
                shape='sphere',
                region=None,
                show_messages=False
            )
            location_object = Location(**location_dict)
            location_object.set_coordinates(target_player)
            location_object.set_radius(5)
            location_object.set_warning_boundary(3)
            try:
                chrani_bot.locations.upsert(location_object, save=True)
            except:
                pass

            chrani_bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
            message = "spawn for player {} created".format(target_player.name)
            logger.debug(message)
            response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "found in the world",
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


def on_player_death(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        try:
            location = chrani_bot.locations.get(target_player.steamid, 'spawn')
            if target_player.authenticated is False:
                location.enabled = False
                message = "spawn for player {} removed, a new one will be created.".format(target_player.name)
                logger.debug(message)
                response_messages.add_message(message, True)
        except KeyError:
            pass

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


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
