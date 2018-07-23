from bot.objects.location import Location
from bot.modules.logger import logger
import common


def on_player_join(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
    except Exception as e:
        logger.exception(e)
        raise KeyError

    try:
        location_object = self.bot.locations.get(player_object.steamid, 'spawn')
    except KeyError:
        location_dict = dict(
            identifier='spawn',
            name='Place of Birth',
            owner=player_object.steamid,
            shape='point',
            radius=None,
            region=None
        )
        location_object = Location(**location_dict)
        location_object.set_coordinates(player_object)
        try:
            self.bot.locations.upsert(location_object, save=True)
        except:
            return False

        logger.debug("spawn for player {} created".format(player_object.name))

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


def on_player_death(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
    except Exception as e:
        logger.exception(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
        if player_object.authenticated is False:
            location.enabled = False
            logger.debug("spawn for player {} removed, a new one will be created".format(player_object.name))
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
