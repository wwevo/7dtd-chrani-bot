import re
from time import time
from bot.player import Player
from bot.logger import logger
from bot.location import Location

actions_dev = []


def fix_players_legs(self):
    """Fixes the legs of the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /fix my legs please

    example:
    /fix my legs please

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.debuffplayer(player_object, "brokenLeg")
        self.tn.debuffplayer(player_object, "sprainedLeg")
        self.tn.send_message_to_player(player_object, "your legs have been taken care of ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "fix my legs please",
        "usage" : "/fix my legs please"
    },
    "action" : fix_players_legs,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def stop_the_bleeding(self):
    """Removes the 'bleeding' buff from the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /make me stop leaking

    example:
    /make me stop leaking

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.debuffplayer(player_object, "bleeding")
        self.tn.send_message_to_player(player_object, "your wounds have been bandaided ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "make me stop leaking",
        "usage" : "/make me stop leaking"
    },
    "action" : stop_the_bleeding,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def apply_first_aid(self):
    """Applies the 'firstAidLarge' buff to the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /heal me up scotty

    example:
    /heal me up scotty

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.buffplayer(player_object, "firstAidLarge")
        self.tn.send_message_to_player(player_object, "feel the power flowing through you!! ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "heal me up scotty",
        "usage" : "/heal me up scotty"
    },
    "action" : apply_first_aid,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def reload_from_db(self):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.bot.load_from_db()
        self.tn.send_message_to_player(player_object, "loaded all from storage!", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "reinitialize",
        "usage" : "/reinitialize"
    },
    "action" : reload_from_db,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def shutdown_bot(self):
    """Shuts down the bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /shut down the matrix

    example:
    /shut down the matrix

    notes:
    Together with a cronjob starting the bot every minute, this can be
    used for restarting it from within the game
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.send_message_to_player(player_object, "bot is shutting down...", color=self.bot.chat_colors['success'])
        self.bot.shutdown_bot()
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "shut down the matrix",
        "usage" : "/shut down the matrix"
    },
    "action" : shutdown_bot,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def obliterate_player(self):
    """Kicks the player and removes all bot-accessible datafor the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /obliterate me

    example:
    /obliterate me

    notes:
    it will delete all locations and all playerdata plus the whitelist entry. Currently it does NOT remove references,
    like if the player is inside a location while obliterated, the location file will not be purged. YET.
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.kick(player_object, "You wanted it! Time to be born again!!")
        location_objects_dict = self.bot.locations.get(player_object.steamid)
        locations_to_remove = []
        for name, location_object in location_objects_dict.iteritems():
            locations_to_remove.append(location_object)

        for location_object in locations_to_remove:
            self.bot.locations.remove(player_object.steamid, location_object.identifier)

        self.bot.players.remove(player_object)
        self.bot.whitelist.remove(player_object)
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "obliterate me",
        "usage" : "/obliterate me"
    },
    "action" : obliterate_player,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def ban_player(self, command):
    """Bans a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /ban player <steamid/entityid> for <ban_reason>

    example:
    /ban player 76561198040658370 for Being an asshat

    notes:
    both the ban-er and the ban-ee will be mentioned in the ban-message
    there is no timeframe, bans are permanent for now
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"ban\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfor\s(?P<ban_reason>.+)", command)
        if p:
            steamid_to_ban = p.group("steamid")
            entityid_to_ban = p.group("entityid")
            if steamid_to_ban is None:
                steamid_to_ban = self.bot.players.entityid_to_steamid(entityid_to_ban)
                if steamid_to_ban is False:
                    raise KeyError

            reason_for_ban = p.group("ban_reason")
            try:
                player_object_to_ban = self.bot.players.get(steamid_to_ban)
            except KeyError:
                player_dict = {'steamid': steamid_to_ban, "name": 'unknown offline player'}
                player_object_to_ban = Player(**player_dict)

            if self.tn.ban(player_object_to_ban, "{} banned {} for {}".format(player_object.name, player_object_to_ban.name, reason_for_ban)):
                self.tn.send_message_to_player(player_object_to_ban, "you have been banned by {}".format(player_object.name), color=self.bot.chat_colors['alert'])
                self.tn.send_message_to_player(player_object, "you have banned player {}".format(player_object_to_ban.name), color=self.bot.chat_colors['success'])
                self.tn.say("{} has been banned by {} for '{}'!".format(player_object_to_ban.name, player_object.name, reason_for_ban), color=self.bot.chat_colors['success'])
            else:
                self.tn.send_message_to_player(player_object, "could not find a player with id {}".format(steamid_to_ban), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "ban player",
        "usage" : "/ban player <steamid/entityid> for <reason>"
    },
    "action" : ban_player,
    "env": "(self, command)",
    "group": "testing",
    "essential" : False
})


def unban_player(self, command):
    """Unbans a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /unban player <steamid/entityid>

    example:
    /unban player 76561198040658370
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"unban\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
        if p:
            steamid_to_unban = p.group("steamid")
            entityid_to_unban = p.group("entityid")
            if steamid_to_unban is None:
                steamid_to_unban = self.bot.players.entityid_to_steamid(entityid_to_unban)

            player_object_to_unban = self.bot.players.load(steamid_to_unban)

            if self.tn.unban(player_object_to_unban):
                self.tn.send_message_to_player(player_object, "you have unbanned player {}".format(player_object_to_unban.name), color=self.bot.chat_colors['success'])
                self.tn.say("{} has been unbanned by {}.".format(player_object_to_unban.name, player_object.name), color=self.bot.chat_colors['success'])
                return True

            self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid_to_unban), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "unban player",
        "usage" : "/unban player <steamid/entityid>"
    },
    "action" : unban_player,
    "env": "(self, command)",
    "group": "testing",
    "essential" : False
})


def kick_player(self, command):
    """Kicks a player

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /kick player <steamid/entityid> for <kick_reason>

    example:
    /kick player 76561198040658370 for Stinking up the room!
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"kick\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfor\s(?P<kick_reason>.+)", command)
        if p:
            steamid_to_kick = p.group("steamid")
            entityid_to_kick = p.group("entityid")
            if steamid_to_kick is None:
                steamid_to_kick = self.bot.players.entityid_to_steamid(entityid_to_kick)

            reason_for_kick = p.group("kick_reason")
            try:
                player_object_to_kick = self.bot.players.get(steamid_to_kick)
            except KeyError:
                self.tn.send_message_to_player(player_object, "could not find a player with id {}".format(steamid_to_kick), color=self.bot.chat_colors['warning'])
                return

            if self.tn.kick(player_object_to_kick, reason_for_kick):
                self.tn.send_message_to_player(player_object, "you have kicked {}".format(player_object_to_kick.name), color=self.bot.chat_colors['success'])
                self.tn.say("{} has been kicked by {} for '{}'!".format(player_object_to_kick.name, player_object.name, reason_for_kick), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "kick player",
        "usage" : "/kick player <steamid/entityid> for <reason>"
    },
    "action" : kick_player,
    "env": "(self, command)",
    "group": "testing",
    "essential" : False
})


def list_online_players(self):
    """Lists all currently online players

    Keyword arguments:
    self -- the bot

    expected bot command:
    /online players

    example:
    /online players

    notes:
    Will list players and show their entityId
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        active_players_dict = self.bot.players.players_dict
        players_to_list = []
        for steamid, player_object_to_list in active_players_dict.iteritems():
            players_to_list.append(player_object_to_list)

        for player_object_to_list in players_to_list:
            self.tn.send_message_to_player(player_object, "{} ([ffffff]{}[-]) / authenticated: {}".format(player_object_to_list.name, player_object_to_list.entityid, str(player_object_to_list.authenticated)), color=self.bot.chat_colors['success'])

    except Exception as e:
        logger.error(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "online players",
        "usage" : "/online players"
    },
    "action" : list_online_players,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def list_available_player_actions(self):
    """Lists all available actions and their usage for the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /list actions

    example:
    /list actions

    notes:
    It will only show the commands the player has access to.
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    available_player_actions = []
    if self.bot.player_actions is not None:
        for player_action in self.bot.player_actions:
            function_category = player_action["group"]
            function_name = getattr(player_action["action"], 'func_name')
            action_string = player_action["command"]["usage"]
            has_permission = self.bot.permissions.player_has_permission(player_object, function_name, function_category)
            if isinstance(has_permission, bool) and has_permission is True:
                available_player_actions.append(action_string)

        self.tn.send_message_to_player(player_object, "The following actions are available to you:", color=self.bot.chat_colors['success'])
        for player_action in available_player_actions:
            self.tn.send_message_to_player(player_object, "{}".format(player_action), color=self.bot.chat_colors['warning'])

    return False


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "list actions",
        "usage" : "/list actions"
    },
    "action" : list_available_player_actions,
    "env": "(self)",
    "group": "testing",
    "essential" : True
})
""" 
here come the observers
"""
observers_dev = []


def record_time_of_last_activity(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        if player_object.is_responsive() is True:
            player_object.last_seen = time()
            self.bot.players.upsert(player_object, save=True)
    except Exception as e:
        logger.error(e)
        pass


observers_dev.append(("monitor", "player is active!", record_time_of_last_activity, "(self)"))


