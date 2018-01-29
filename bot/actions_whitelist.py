from player import Player
import re


actions_whitelist = []


def add_player_to_whitelist(self, players, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"add\s(?P<steamid>.+)\sto whitelist", command)
        if p:
            steamid = p.group("steamid")
            player_object_to_whitelist = players.get(steamid)
            if player_object_to_whitelist is False:
                player_dict = {'steamid': steamid, "name": 'unknown offline player'}
                player_object_to_whitelist = Player(**player_dict)
            if self.bot.whitelist.upsert(player_object, player_object_to_whitelist, save=True):
                self.tn.send_message_to_player(player_object_to_whitelist, "you have been whitelisted by {}".format(player_object.name))
            else:
                self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid))
            self.tn.send_message_to_player(player_object, "you have whitelisted {}".format(steamid))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("startswith", "add", add_player_to_whitelist, "(self, players, command)"))


def activate_whitelist(self, players):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        self.bot.whitelist.activate()
        self.tn.say("whitelist is in effect! feeling safer already :)")
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("isequal", "activate whitelist", activate_whitelist, "(self, players)"))


"""
here come the observers
"""
observers_whitelist = []


def player_set_to_online(self, players):
    """
    When a player trying to join
    :param self:
    :param player_object:
    :return:
    """
    player_object = players.get(self.player_steamid)
    if self.bot.whitelist.is_active() and not self.bot.whitelist.player_is_allowed(player_object):
        self.tn.kick(player_object, "You are not on our whitelist! Visit chrani.net/chrani-bot to find out what that means!")


observers_whitelist.append(("set to online", player_set_to_online, "(self, players)"))
