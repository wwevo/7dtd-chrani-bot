import re
from location import Location

actions_authentication = []


def password(self, players, command):
    player_object = players.get(self.player_steamid)
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
        players.save(player_object)


actions_authentication.append(("startswith", "password", password, "(self, players, command)"))


def on_player_join(self, players, locations):
    player_object = players.get(self.player_steamid)
    """
    When a player is joining
    :param self:
    :param locations:
    :return:
    """
    try:
        location = locations.get(player_object.steamid, 'spawn')
        self.tn.send_message_to_player(player_object, "Welcome back " + player_object.name + " o/")
    except KeyError:
        self.tn.send_message_to_player(player_object, "this servers bot says Hi to " + player_object.name + " o/")
        location_dict = dict(
            name='spawn',
            owner=player_object.steamid,
            pos_x=int(player_object.pos_x),
            pos_y=int(player_object.pos_y),
            pos_z=int(player_object.pos_z),
            shape='point',
            radius=None,
            region=[player_object.region]
        )
        locations.add(Location(**location_dict), save=True)

    if not player_object.authenticated:
        self.tn.send_message_to_player(player_object, "read the rules on https://chrani.net/chrani-bot")


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self, players, locations)"))


