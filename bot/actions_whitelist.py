import re
import urllib

from bot.command_line_args import args_dict
from bot.logger import logger
from bot.player import Player

actions_whitelist = []


def add_player_to_whitelist(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"add\s(?P<steamid>.+)\sto whitelist", command)
    if p:
        steamid_to_whitelist = p.group("steamid")
        try:
            player_object_to_whitelist = self.bot.players.get(steamid_to_whitelist)
        except KeyError:
            player_dict = {'steamid': steamid_to_whitelist, "name": 'unknown offline player'}
            player_object_to_whitelist = Player(**player_dict)

        if self.bot.whitelist.add(player_object, player_object_to_whitelist, save=True):
            self.tn.send_message_to_player(player_object_to_whitelist, "you have been whitelisted by {}".format(player_object.name))
        else:
            self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid_to_whitelist))
        self.tn.send_message_to_player(player_object, "you have whitelisted {}".format(steamid_to_whitelist))


actions_whitelist.append(("startswith", "add", add_player_to_whitelist, "(self, command)", "whitelist"))


def remove_player_from_whitelist(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"remove\s(?P<steamid>.+)\sfrom whitelist", command)
    if p:
        steamid_to_dewhitelist = p.group("steamid")
        try:
            player_object_to_dewhitelist = self.bot.players.get(steamid_to_dewhitelist)
        except KeyError:
            player_dict = {'steamid': steamid_to_dewhitelist}
            player_object_to_dewhitelist = Player(**player_dict)

        if self.bot.whitelist.remove(player_object_to_dewhitelist):
            self.tn.send_message_to_player(player_object_to_dewhitelist, "you have been de-whitelisted by {}".format(player_object.name))
        else:
            self.tn.send_message_to_player(player_object, "could not find a player with steamid '{}' on the whitelist".format(steamid_to_dewhitelist))
            return False
        self.tn.send_message_to_player(player_object, "you have de-whitelisted {}".format(steamid_to_dewhitelist))


actions_whitelist.append(("startswith", "remove", remove_player_from_whitelist, "(self, command)", "whitelist"))


def activate_whitelist(self):
    self.bot.whitelist.activate()
    self.tn.say("Whitelist is in effect! Feeling safer already :)")


actions_whitelist.append(("isequal", "activate whitelist", activate_whitelist, "(self)", "whitelist"))


def deactivate_whitelist(self):
    self.bot.whitelist.deactivate()
    self.tn.say("Whitelist has been disabled. We are feeling adventureous :)")


actions_whitelist.append(("isequal", "deactivate whitelist", deactivate_whitelist, "(self)", "whitelist"))


"""
here come the observers
"""
observers_whitelist = []


def check_if_player_is_on_whitelist(self, player_object=None):
    if player_object is None:
        player_object = self.bot.players.get(self.player_steamid)
    else:
        called_by_trigger = True
        self.bot = self
        try:
            player_object = self.bot.players.load(player_object.steamid)
        except KeyError:
            pass

    if self.bot.whitelist.is_active():
        if not self.bot.whitelist.player_is_allowed(player_object):
            logger.info("kicked player {} for not being on the whitelist".format(player_object.name))
            self.tn.say("{} has been kicked. This is VIP Only!".format(player_object.name))
            self.tn.kick(player_object, "You are not on our whitelist. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")


observers_whitelist.append(("monitor", "set to online", check_if_player_is_on_whitelist, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_if_player_is_on_whitelist, "(self, player_object)"))


def check_if_player_has_url_name(self, player_object=None):
    if player_object is None:
        player_object = self.bot.players.get(self.player_steamid)
    else:
        called_by_trigger = True
        self.bot = self

    if not self.bot.whitelist.player_is_allowed(player_object):
        p = re.search(r"[-A-Z0-9+&@#/%?=~_|!:,.;]{3,}\.[A-Z0-9+&@#/%=~_|]{2,3}", player_object.name, re.IGNORECASE)
        if p:
            logger.info("kicked player {} for having an URL in the name.".format(player_object.name))
            self.tn.say("{} has been kicked. crappy url-name!".format(player_object.steamid))
            self.tn.kick(player_object, "We do not allow urls in names. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")


observers_whitelist.append(("monitor", "set to online", check_if_player_has_url_name, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_if_player_has_url_name, "(self, player_object)"))


def check_ip_country(self, player_object=None):
    if str(args_dict['IP-Token']) == 'dummy':
        return
    if player_object is None:
        player_object = self.bot.players.get(self.player_steamid)
    else:
        called_by_trigger = True
        self.bot = self

    users_country = player_object.get_country_code()
    if self.bot.whitelist.player_is_allowed(player_object) or (users_country is not None and users_country not in self.bot.banned_countries_list):
        pass
    else:
        try:
            f = urllib.urlopen("https://ipinfo.io/" + player_object.ip + "/country?token=" + str(args_dict['IP-Token']))
            users_country = f.read().rstrip()
            if users_country in self.bot.banned_countries_list:
                logger.info("kicked player {} for being from {}".format(player_object.name, users_country))
                self.tn.say("{} has been kicked. Blacklisted Country ({})!".format(player_object.name, users_country))
                self.tn.kick(player_object, "Your IP seems to be from a blacklisted country. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")
            else:
                player_object.set_country_code(users_country)
                self.bot.players.upsert(player_object, save=True)
        except Exception:
            pass


observers_whitelist.append(("monitor", "set to online", check_ip_country, "(self)"))
observers_whitelist.append(("trigger", "set to online", check_ip_country, "(self, player_object)"))

