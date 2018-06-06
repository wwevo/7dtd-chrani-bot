from bot.location import Location
from bot.logger import logger

actions_spawn = []


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    self.tn.send_message_to_player(player_object, "{} is ready and listening (v{})".format(self.bot.bot_name, self.bot.bot_version), color=self.bot.chat_colors['info'])

    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
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

        self.tn.send_message_to_player(player_object, "your place of origin has been recorded ^^", color=self.bot.chat_colors['background'])

    return True


actions_spawn.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "entered the stream",
        "usage" : None
    },
    "action" : on_player_join,
    "env": "(self)",
    "group": "spawn",
    "essential" : True
})


def on_player_death(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
        if player_object.authenticated is False:
            self.bot.locations.remove(player_object.steamid, 'spawn')
            logger.debug("spawn for player {} removed, a new one will be created".format(player_object.name))
    except KeyError:
        return

    return True


actions_spawn.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "died",
        "usage" : None
    },
    "action" : on_player_death,
    "env": "(self)",
    "group": "spawn",
    "essential" : True
})

"""
here come the observers
"""
# no observers, they are all generic and found in actions_locations
