import re
import urllib

from bot.assorted_functions import ObjectView
from bot.modules.logger import logger
import common


def add_player_to_whitelist(bot, source_player, target_player, command):
    try:
        p = re.search(r"add\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sto whitelist", command)
        if p:
            steamid_to_whitelist = p.group("steamid")
            entityid_to_whitelist = p.group("entityid")
            if steamid_to_whitelist is None:
                steamid_to_whitelist = bot.players.entityid_to_steamid(entityid_to_whitelist)
                if steamid_to_whitelist is False:
                    raise KeyError

            try:
                target_player = bot.players.get_by_steamid(steamid_to_whitelist)
                player_dict_to_whitelist = {
                    "steamid": target_player.steamid,
                    "name": target_player.name
                }
            except KeyError:
                player_dict_to_whitelist = {
                    "steamid": steamid_to_whitelist,
                    "name": 'unknown offline player'
                }

            if not bot.whitelist.add(target_player, player_dict_to_whitelist):
                bot.tn.send_message_to_player(target_player, "could not find a player with steamid {}".format(steamid_to_whitelist), color=bot.chat_colors['warning'])
                return False

            bot.tn.send_message_to_player(target_player, "you have whitelisted {}".format(player_dict_to_whitelist["name"]), color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "add player",
        "usage": "/add player <steamid/entityid> to whitelist"
    },
    "action": add_player_to_whitelist,
    "env": "(self, command)",
    "group": "whitelist",
    "essential": False
})


def remove_player_from_whitelist(bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfrom whitelist", command)
        if p:
            steamid_to_dewhitelist = p.group("steamid")
            entityid_to_dewhitelist = p.group("entityid")
            if steamid_to_dewhitelist is None:
                steamid_to_dewhitelist = bot.players.entityid_to_steamid(entityid_to_dewhitelist)
                if steamid_to_dewhitelist is False:
                    raise KeyError

            player_dict = ObjectView
            try:
                player_object_to_dewhitelist = bot.players.get_by_steamid(steamid_to_dewhitelist)
                player_dict.steamid = player_object_to_dewhitelist.steamid
                player_dict.name = player_object_to_dewhitelist.name
            except KeyError:
                player_dict.steamid = steamid_to_dewhitelist
                player_dict.name = 'unknown offline player'
                player_object_to_dewhitelist = player_dict

            if bot.whitelist.remove(player_object_to_dewhitelist):
                bot.tn.send_message_to_player(player_object_to_dewhitelist, "you have been de-whitelisted by {}".format(target_player.name), color=bot.chat_colors['alert'])
            else:
                bot.tn.send_message_to_player(target_player, "could not find a player with steamid '{}' on the whitelist".format(steamid_to_dewhitelist), color=bot.chat_colors['warning'])
                return False
            bot.tn.send_message_to_player(target_player, "you have de-whitelisted {}".format(player_object_to_dewhitelist.name), color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "remove player",
        "usage": "/remove player <steamid/entityid> from whitelist"
    },
    "action": remove_player_from_whitelist,
    "env": "(self, command)",
    "group": "whitelist",
    "essential": False
})


def activate_whitelist(bot, source_player, target_player, command):
    try:
        bot.whitelist.activate()
        bot.tn.say("Whitelist is in effect! Feeling safer already :)", color=bot.chat_colors['alert'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "activate whitelist",
        "usage": "/activate whitelist"
    },
    "action": activate_whitelist,
    "env": "(self)",
    "group": "whitelist",
    "essential": False
})


def deactivate_whitelist(bot, source_player, target_player, command):
    try:
        bot.whitelist.deactivate()
        bot.tn.say("Whitelist has been disabled. We are feeling adventureous :)", color=bot.chat_colors['alert'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "deactivate whitelist",
        "usage": "/deactivate whitelist"
    },
    "action": deactivate_whitelist,
    "env": "(self)",
    "group": "whitelist",
    "essential": False
})
"""
here come the observers
# these whitelist functions are special because they run as a monitor AND are used as triggers during login, to catch players before they even enter the game
"""


def check_if_player_is_on_whitelist(self, player_object=None):
    try:
        if player_object is None:
            player_object = self.bot.players.get_by_steamid(self.player_steamid)
        else:
            logger.debug("checking player {} for being on the whitelist".format(player_object.name))
            called_by_trigger = True
            self.bot = self
            try:
                player_object = self.bot.players.load(player_object.steamid)
            except KeyError as e:
                return

        if self.bot.whitelist.is_active() is True:
            if not self.bot.whitelist.player_is_allowed(player_object):
                logger.info("kicked player {} for not being on the whitelist".format(player_object.name))
                self.tn.say("{} has been kicked. This is VIP Only!".format(player_object.name), color=self.bot.chat_colors['alert'])
                self.tn.kick(player_object, "You are not on our whitelist. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "set to online",
    "action": check_if_player_is_on_whitelist,
    "env": "(self)",
    "essential": True
})

common.observers_list.append({
    "type": "trigger",
    "title": "set to online",
    "action": check_if_player_is_on_whitelist,
    "env": "(self, player_object)",
    "essential": True
})


def check_if_player_has_url_name(self, player_object=None):
    try:
        if player_object is None:
            player_object = self.bot.players.get_by_steamid(self.player_steamid)
        else:
            logger.debug("checking player {} for having a 'bad' username".format(player_object.name))
            called_by_trigger = True
            self.bot = self

        if not self.bot.whitelist.player_is_allowed(player_object):
            p = re.search(r"[-A-Z0-9+&@#/%?=~_|!:,.;]{3,}\.[A-Z0-9+&@#/%=~_|]{2,3}$", player_object.name, re.IGNORECASE)
            if p:
                logger.info("kicked player {} for having an URL in the name.".format(player_object.name))
                self.tn.say("{} has been kicked. we do not allow url-names!".format(player_object.steamid), color=self.bot.chat_colors['alert'])
                self.tn.kick(player_object, "We do not allow urls in names. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "set to online",
    "action": check_if_player_has_url_name,
    "env": "(self)",
    "essential": True
})

common.observers_list.append({
    "type": "trigger",
    "title": "set to online",
    "action": check_if_player_has_url_name,
    "env": "(self, player_object)",
    "essential": True
})


def check_ip_country(self, player_object=None):
    try:
        if self.bot.settings.get_setting_by_name('ipinfo.io_password') is None:
            return
        if player_object is None:
            player_object = self.bot.players.get_by_steamid(self.player_steamid)
        else:
            # the scope changes when called by the bots main-loop
            logger.debug("checking player {} for being from blacklisted countries".format(player_object.name))
            called_by_trigger = True
            self.bot = self

        # check if we already know the country code and check against whitelist and banned list
        users_country = player_object.get_country_code()
        if self.bot.whitelist.player_is_allowed(player_object) or (users_country is not None and users_country not in self.bot.banned_countries_list):
            return False

        try:
            if users_country is None:
                f = urllib.urlopen("https://ipinfo.io/" + player_object.ip + "/country?token=" + str(self.bot.settings.get_setting_by_name('ipinfo.io_password')))
                users_country = f.read().rstrip()
        except Exception:
            logger.debug("something went wrong in fetching the ipinfo dataset for player {}".format(player_object.name))

        try:
            player_object.set_country_code(users_country)
            self.bot.players.upsert(player_object, save=True)
        except Exception as e:
            logger.exception(e)

        if users_country in self.bot.banned_countries_list and player_object.is_blacklisted() is False:
            if self.tn.kick(player_object, "Your IP seems to be from a blacklisted country. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!"):
                player_object.blacklisted = True
                logger.info("kicked player {} for being from {}".format(player_object.name, users_country))
                self.tn.say("{} has been kicked. Blacklisted Country ({})!".format(player_object.name, users_country), color=self.bot.chat_colors['alert'])

    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "set to online",
    "action": check_ip_country,
    "env": "(self)",
    "essential": True
})

common.observers_list.append({
    "type": "trigger",
    "title": "set to online",
    "action": check_ip_country,
    "env": "(self, player_object)",
    "essential": True
})
