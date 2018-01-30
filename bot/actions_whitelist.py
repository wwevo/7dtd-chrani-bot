from bot.command_line_args import args_dict
from player import Player
from logger import logger
import re, urllib


actions_whitelist = []


def add_player_to_whitelist(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        p = re.search(r"add\s(?P<steamid>.+)\sto whitelist", command)
        if p:
            steamid_to_whitelist = p.group("steamid")
            try:
                player_object_to_whitelist = self.bot.players.get(steamid_to_whitelist)
            except KeyError:
                player_dict = {'steamid': steamid_to_whitelist, "name": 'unknown offline player'}
                player_object_to_whitelist = Player(**player_dict)

            if self.bot.whitelist.upsert(player_object, player_object_to_whitelist, save=True):
                self.tn.send_message_to_player(player_object_to_whitelist, "you have been whitelisted by {}".format(player_object.name))
            else:
                self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid_to_whitelist))
            self.tn.send_message_to_player(player_object, "you have whitelisted {}".format(steamid_to_whitelist))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("startswith", "add", add_player_to_whitelist, "(self, command)"))


def activate_whitelist(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        self.bot.whitelist.activate()
        self.tn.say("whitelist is in effect! feeling safer already :)")
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("isequal", "activate whitelist", activate_whitelist, "(self)"))


"""
here come the observers
"""
observers_whitelist = []


def check_if_player_is_on_whitelist(self):
    """
    When a player trying to join
    :param self:
    :param player_object:
    :return:
    """
    player_object = self.bot.players.get(self.player_steamid)
    if self.bot.whitelist.is_active() and not self.bot.whitelist.player_is_allowed(player_object):
        logger.info("kicked player {} for not being on the whitelist".format(player_object.name))
        self.tn.say("{} has been kicked. This is VIP Only!".format(player_object.name))
        self.tn.kick(player_object, "You are not on our whitelist. Visit chrani.net/chrani-bot to find out what that means and if / what options are available for you!")


observers_whitelist.append(("set to online", check_if_player_is_on_whitelist, "(self)"))


def check_if_player_has_url_name(self):
    player_object = self.bot.players.get(self.player_steamid)
    if not self.bot.whitelist.player_is_allowed(player_object):
        p = re.search(r"[-A-Z0-9+&@#/%?=~_|!:,.;]{3,}\.[A-Z0-9+&@#/%=~_|]{2,3}", player_object.name, re.IGNORECASE)
        if p:
            logger.info("kicked player {} for having an URL in the name.".format(player_object.name))
            self.tn.say("{} has been kicked. crappy url-name!".format(player_object.steamid))
            self.tn.kick(player_object, "We do not allow urls in names. Visit chrani.net/chrani-bot to find out what that means and if / what options are available for you!")


observers_whitelist.append(("set to online", check_if_player_has_url_name, "(self)"))


def check_ip_country(self):
    if str(args_dict['IP-Token']) == 'dummy':
        logger.info("IP check disabled for local testing")
        return
    player_object = self.bot.players.get(self.player_steamid)
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
                self.tn.kick(player_object, "Your IP seems to be from a blacklisted country. Visit chrani.net/chrani-bot to find out what that means and if / what options are available for you!")
            else:
                player_object.set_country_code(users_country)
                self.bot.players.upsert(player_object, save=True)
        except Exception:
            pass


observers_whitelist.append(("set to online", check_ip_country, "(self)"))



