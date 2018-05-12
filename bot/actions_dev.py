import re
from time import time
from bot.player import Player
from bot.logger import logger
from bot.location import Location

actions_dev = []


def fix_players_legs(self):
    """Fixes the legs of the player isuing this action

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


actions_dev.append(("isequal", ["fix my legs please", "/fix my legs please"], fix_players_legs, "(self)", "testing"))


def stop_the_bleeding(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.debuffplayer(player_object, "bleeding")
        self.tn.send_message_to_player(player_object, "your wounds have been bandaided ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append(("isequal", ["make me stop leaking", "/make me stop leaking"], stop_the_bleeding, "(self)", "testing"))


def apply_first_aid(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.buffplayer(player_object, "firstAidLarge")
        self.tn.send_message_to_player(player_object, "feel the power flowing through you!! ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append(("isequal", ["heal me up scotty", "/heal me up scotty"], apply_first_aid, "(self)", "testing"))


def reload_from_db(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.bot.load_from_db()
        self.tn.send_message_to_player(player_object, "loaded all from storage!", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append(("isequal", ["reinitialize", "/reinitialize"], reload_from_db, "(self)", "testing"))


def shutdown_bot(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.send_message_to_player(player_object, "bot is shutting down...", color=self.bot.chat_colors['success'])
        self.bot.shutdown_bot()
    except Exception as e:
        logger.error(e)
        pass


actions_dev.append(("isequal", ["shut down the matrix", "/shut down the matrix"], shutdown_bot, "(self)", "testing"))


def obliterate_player(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        player_object.switch_off("suicide")
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


actions_dev.append(("isequal", ["obliterate me", "/obliterate me"], obliterate_player, "(self)", "testing"))


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


actions_dev.append(("startswith", ["ban player", "/ban player <steamid/entityid> for <reason>"], ban_player, "(self, command)", "testing"))


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


actions_dev.append(("startswith", ["unban player", "/unban player <steamid/entityid>"], unban_player, "(self, command)", "testing"))


def kick_player(self, command):
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


actions_dev.append(("startswith", ["kick player", "/kick player <steamid/entityid> for <reason>"], kick_player, "(self, command)", "testing"))


def list_online_players(self):
    try:
        active_players_dict = self.bot.players.players_dict
        players_to_list = []
        for steamid, player_object in active_players_dict.iteritems():
            players_to_list.append(player_object)

        for player_object in players_to_list:
            self.tn.say("{} ([ffffff]{}[-]) / authenticated: {}".format(player_object.name, player_object.entityid, str(player_object.authenticated)), color=self.bot.chat_colors['success'])

    except Exception as e:
        logger.error(e)
        pass


actions_dev.append(("isequal", ["online players", "/online players"], list_online_players, "(self)", "testing"))


def list_available_player_actions(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    available_player_actions = []
    if self.bot.player_actions is not None:
        for player_action in self.bot.player_actions:
            function_category = player_action[4]
            function_name = getattr(player_action[2], 'func_name')
            action_string = player_action[1][1]
            has_permission = self.bot.permissions.player_has_permission(player_object, function_name, function_category)
            if isinstance(has_permission, bool) and has_permission is True:
                available_player_actions.append(action_string)

        self.tn.send_message_to_player(player_object, "The following actions are available to you:", color=self.bot.chat_colors['success'])
        for player_action in available_player_actions:
            self.tn.send_message_to_player(player_object, "{}".format(player_action), color=self.bot.chat_colors['warning'])

    return False


actions_dev.append(("isequal", ["list actions", "/list actions"], list_available_player_actions, "(self)", "testing"))


def on_player_death(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
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


actions_dev.append(("isequal", ["died", "died"], on_player_death, "(self)", "backpack", True))
""" 
here come the observers
"""
observers_dev = []


def record_time_of_last_activity(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        if player_object.is_responsive is True:
            player_object.last_seen = time()
            self.bot.players.upsert(player_object, save=True)
    except Exception as e:
        logger.error(e)
        pass


observers_dev.append(("monitor", "player is active!", record_time_of_last_activity, "(self)"))


