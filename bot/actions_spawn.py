from bot.location import Location
from bot.logger import logger

actions_spawn = []


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
    except KeyError:
        location_dict = dict(
            identifier='spawn',
            name='Place of Birth',
            owner=player_object.steamid,
            shape='point',
            radius=None,
            region=[player_object.region]
        )
        location_object = Location(**location_dict)
        location_object.set_coordinates(player_object)
        self.bot.locations.upsert(location_object, save=True)
        self.tn.send_message_to_player(player_object, "your place of origin has been recorded ^^", color=self.bot.chat_colors['background'])

    return True


actions_spawn.append(("isequal", "joined the game", on_player_join, "(self)", "spawn"))


"""
here come the observers
"""
# no observers, they are all generic and found in actions_locations
