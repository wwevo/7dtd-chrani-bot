from whitelist import Whitelist
import re

whitelist = Whitelist()


actions_whitelist = []


def add_player_to_whitelist(self, players, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"add\s(?P<steamid>.+)\sto whitelist", command)
        if p:
            steamid = p.group("steamid")
            try:
                player_object_to_whitelist = self.bot.players_dict[steamid]
                whitelist.add_player(player_object_to_whitelist)
                self.tn.send_message_to_player(player_object_to_whitelist, "you have been whitelisted by {}".format(player_object.name))
            except KeyError:
                if whitelist.add_player_by_steamid(steamid):
                    self.tn.send_message_to_player(player_object, "you have whitelisted {}".format(steamid))
                else:
                    self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("startswith", "add", add_player_to_whitelist, "(self, players, command)"))


def remove_player_from_whitelist(self, players, command):
    player_object = players.get(self.player_steamid)
    if player_object.authenticated:
        p = re.search(r"remove\s(?P<steamid>.+)\sfrom whitelist", command)
        if p:
            steamid = p.group("steamid")
            try:
                player_object_in_whitelist = self.bot.players_dict[steamid]
                whitelist.remove_player(player_object_in_whitelist)
                self.tn.send_message_to_player(player_object_in_whitelist, "you have been removed from the whitelist by {}".format(player_object.name))
            except KeyError:
                if whitelist.remove_player_by_steamid(steamid):
                    self.tn.send_message_to_player(player_object, "you have removed player {} from the whitelist!".format(steamid))
                else:
                    self.tn.send_message_to_player(player_object, "could not find a player with steamid {}".format(steamid))
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_whitelist.append(("startswith", "remove", remove_player_from_whitelist, "(self, players, command)"))

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
    if whitelist.is_active() and not whitelist.player_is_allowed(player_object):
        self.tn.kick(player_object, "You are not on our whitelist! Visit chrani.net/chrani-bot to find out what that means!")


observers_whitelist.append(("set to online", player_set_to_online, "(self, players)"))
