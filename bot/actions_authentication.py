import re
from location import Location

actions_authentication = []


def password(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"password (.+)", command)
    if p:
        pwd = p.group(1)
        if pwd == "openup":
            if player_object.authenticated is True:
                self.tn.send_message_to_player(player_object, player_object.name + ", we trust you already <3")
            else:
                self.tn.send_message_to_player(player_object, player_object.name + " joined the ranks of literate people. Welcome!")
                player_object.set_authenticated(True)
        else:
            player_object.set_authenticated(False)
            self.tn.say(player_object.name + " has entered a wrong password oO!")
        self.bot.players.upsert(player_object, save=True)


actions_authentication.append(("startswith", "password", password, "(self, command)"))


def on_player_join(self):
    player_object = self.bot.players.get(self.player_steamid)
    """
    When a player is joining
    :param self:
    :param locations:
    :return:
    """
    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
        self.tn.send_message_to_player(player_object, "Welcome back " + player_object.name + " o/")
    except KeyError:
        self.tn.send_message_to_player(player_object, "this servers bot says Hi to " + player_object.name + " o/")
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

    if player_object.authenticated is not True:
        self.tn.send_message_to_player(player_object, "read the rules on https://chrani.net/chrani-bot")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self)"))


