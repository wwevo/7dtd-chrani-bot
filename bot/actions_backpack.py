from bot.logger import logger
from bot.location import Location

actions_backpack = []


def on_player_death(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.exception(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'death')
    except KeyError:
        location_dict = dict(
            identifier='death',
            name='Place of Death',
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

        self.tn.send_message_to_player(player_object, "your place of death has been recorded ^^", color=self.bot.chat_colors['background'])

    return True


actions_backpack.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "died",
        "usage" : None
    },
    "action" : on_player_death,
    "env": "(self)",
    "group": "backpack",
    "essential" : True
})


def on_player_kill(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.exception(e)
        raise KeyError

    try:
        location = self.bot.locations.get(player_object.steamid, 'death')
    except KeyError:
        location_dict = dict(
            identifier='death',
            name='Place of Death',
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

        self.tn.send_message_to_player(player_object, "your place of death has been recorded ^^", color=self.bot.chat_colors['background'])

    return True


actions_backpack.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "killed by",
        "usage" : None
    },
    "action" : on_player_kill,
    "env": "(self)",
    "group": "backpack",
    "essential" : True
})


def take_me_to_my_backpack(self):
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
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "death")
            if location_object.player_is_inside_boundary(player_object):
                self.tn.send_message_to_player(player_object, "eh, you already ARE near your pack oO".format(player_object.name), color=self.bot.chat_colors['warning'])
            else:
                self.tn.teleportplayer(player_object, location_object=location_object)
                self.tn.say("{} can't live without their stuff".format(player_object.name), color=self.bot.chat_colors['background'])

            self.bot.locations.remove(player_object.steamid, 'death')

        except KeyError:
            self.tn.send_message_to_player(player_object, "I don't have your last death on record, sorry :(".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


actions_backpack.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "take me to my pack",
        "usage" : "/take me to my pack"
    },
    "action" : take_me_to_my_backpack,
    "env": "(self)",
    "group": "backpack",
    "essential" : False
})
