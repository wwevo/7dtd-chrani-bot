import re
import urllib

from bot.logger import logger
from bot.player import Player

actions_whitelist = []


def add_player_to_whitelist(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"add\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sto whitelist", command)
        if p:
            steamid_to_whitelist = p.group("steamid")
            entityid_to_whitelist = p.group("entityid")
            if steamid_to_whitelist is None:
                steamid_to_whitelist = self.bot.players.entityid_to_steamid(entityid_to_whitelist)
                if steamid_to_whitelist is False:
                    raise KeyError

            try:
                player_object_to_whitelist = self.bot.players.get(steamid_to_whitelist)
            except KeyError:
                player_dict = {'steamid': steamid_to_whitelist, "name": 'unknown offline player'}
                player_object_to_whitelist = Player(**player_dict)

            if self.bot.whitelist.add(player_object, player_object_to_whitelist, save=True):
                self.tn.send_message_to_player(player_object_to_whitelist, "you have been whitelisted by {}".format(player_object.name), color=self.bot.chat_colors['alert'])
            else:
                self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid_to_whitelist), color=self.bot.chat_colors['warning'])
            self.tn.send_message_to_player(player_object, "you have whitelisted {}".format(player_object_to_whitelist.name), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_whitelist.append(("startswith", "add player", add_player_to_whitelist, "(self, command)", "whitelist"))


def remove_player_from_whitelist(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"remove\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfrom whitelist", command)
        if p:
            steamid_to_dewhitelist = p.group("steamid")
            entityid_to_dewhitelist = p.group("entityid")
            if steamid_to_dewhitelist is None:
                steamid_to_dewhitelist = self.bot.players.entityid_to_steamid(entityid_to_dewhitelist)
                if steamid_to_dewhitelist is False:
                    raise KeyError

            try:
                player_object_to_dewhitelist = self.bot.players.get(steamid_to_dewhitelist)
            except KeyError:
                player_dict = {'steamid': steamid_to_dewhitelist}
                player_object_to_dewhitelist = Player(**player_dict)

            if self.bot.whitelist.remove(player_object_to_dewhitelist):
                self.tn.send_message_to_player(player_object_to_dewhitelist, "you have been de-whitelisted by {}".format(player_object.name), color=self.bot.chat_colors['alert'])
            else:
                self.tn.send_message_to_player(player_object, "could not find a player with steamid '{}' on the whitelist".format(steamid_to_dewhitelist), color=self.bot.chat_colors['warning'])
                return False
            self.tn.send_message_to_player(player_object, "you have de-whitelisted {}".format(player_object_to_dewhitelist.name), color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_whitelist.append(("startswith", "remove player", remove_player_from_whitelist, "(self, command)", "whitelist"))


def activate_whitelist(self):
    try:
        self.bot.whitelist.activate()
        self.tn.say("Whitelist is in effect! Feeling safer already :)", color=self.bot.chat_colors['alert'])
    except Exception as e:
        logger.error(e)
        pass


actions_whitelist.append(("isequal", "activate whitelist", activate_whitelist, "(self)", "whitelist"))


def deactivate_whitelist(self):
    try:
        self.bot.whitelist.deactivate()
        self.tn.say("Whitelist has been disabled. We are feeling adventureous :)", color=self.bot.chat_colors['alert'])
    except Exception as e:
        logger.error(e)
        pass


actions_whitelist.append(("isequal", "deactivate whitelist", deactivate_whitelist, "(self)", "whitelist"))


"""
here come the observers
# these whitelist functions are special because they run as a monitor AND are used as triggers during login, to catch players before they even enter the game
"""
observers_whitelist = []


def check_if_player_is_on_whitelist(self, player_object=None):
    try:
        if player_object is None:
            player_object = self.bot.players.get(self.player_steamid)
        else:
            called_by_trigger = True
            self.bot = self
            try:
                player_object = self.bot.players.load(player_object.steamid)
            except KeyError as e:
                logger.error("{} encountered the error '{}'".format(player_object.name, e))

        if self.bot.whitelist.is_active():
            if not self.bot.whitelist.player_is_allowed(player_object):
                logger.info("kicked player {} for not being on the whitelist".format(player_object.name))
                self.tn.say("{} has been kicked. This is VIP Only!".format(player_object.name), color=self.bot.chat_colors['alert'])
                self.tn.kick(player_object, "You are not on our whitelist. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")
    except Exception as e:
        logger.error("{} encountered the error '{}'".format(player_object.name, e))
        pass


observers_whitelist.append(("monitor", "set to online", check_if_player_is_on_whitelist, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_if_player_is_on_whitelist, "(self, player_object)"))


def check_if_player_has_url_name(self, player_object=None):
    try:
        if player_object is None:
            player_object = self.bot.players.get(self.player_steamid)
        else:
            called_by_trigger = True
            self.bot = self

        if not self.bot.whitelist.player_is_allowed(player_object):
            p = re.search(r"[-A-Z0-9+&@#/%?=~_|!:,.;]{3,}\.[A-Z0-9+&@#/%=~_|]{2,3}$", player_object.name, re.IGNORECASE)
            if p:
                logger.info("kicked player {} for having an URL in the name.".format(player_object.name))
                self.tn.say("{} has been kicked. we do not allow url-names!".format(player_object.steamid), color=self.bot.chat_colors['alert'])
                self.tn.kick(player_object, "We do not allow urls in names. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")
    except Exception as e:
        logger.error("{} encountered the error '{}'".format(player_object.name, e))
        pass


observers_whitelist.append(("monitor", "set to online", check_if_player_has_url_name, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_if_player_has_url_name, "(self, player_object)"))


def check_ip_country(self, player_object=None):
    try:
        if self.bot.settings_dict['ipinfo.io_password'] is None:
            return
        if player_object is None:
            player_object = self.bot.players.get(self.player_steamid)
        else:
            # the scope changes when called by the bots main-loop
            called_by_trigger = True
            self.bot = self

        # check if we already know the country code and check against whitelist and banned list
        users_country = player_object.get_country_code()
        if self.bot.whitelist.player_is_allowed(player_object) or (users_country is not None and users_country not in self.bot.banned_countries_list):
            return False

        try:
            if users_country is None:
                f = urllib.urlopen("https://ipinfo.io/" + player_object.ip + "/country?token=" + str(self.bot.settings_dict['ipinfo.io_password']))
                users_country = f.read().rstrip()
        except Exception:
            logger.debug("something went wrong in fetching the ipinfo dataset for player {}".format(player_object.name))

        try:
            player_object.set_country_code(users_country)
            self.bot.players.upsert(player_object, save=True)
        except Exception as e:
            logger.error("{} encountered the error '{}'".format(player_object.name, e))

        if users_country in self.bot.banned_countries_list:
            if self.tn.kick(player_object, "Your IP seems to be from a blacklisted country. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!"):
                logger.info("kicked player {} for being from {}".format(player_object.name, users_country))
                self.tn.say("{} has been kicked. Blacklisted Country ({})!".format(player_object.name, users_country), color=self.bot.chat_colors['alert'])

    except Exception as e:
        logger.error("{} encountered the error '{}'".format(player_object.name, e))
        pass


observers_whitelist.append(("monitor", "set to online", check_ip_country, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_ip_country, "(self, player_object)"))
