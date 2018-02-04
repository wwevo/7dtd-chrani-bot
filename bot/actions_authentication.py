import re
from bot.location import Location

actions_authentication = []


def password(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"password (.+)", command)
    if p:
        pwd = p.group(1)
        if pwd == "openup":
            if player_object.authenticated is True:
                self.tn.send_message_to_player(player_object, "{} we trust you already <3".format(player_object.name))
            else:
                self.tn.send_message_to_player(player_object, "{} joined the ranks of literate people. Welcome!".format(player_object.name))
                player_object.set_authenticated(True)
                player_object.add_permission_level("authenticated")
        else:
            player_object.set_authenticated(False)
            self.tn.say("{} has entered a wrong password oO!".format(player_object.name))
            player_object.set_permission_levels([])

        self.bot.players.upsert(player_object, save=True)


actions_authentication.append(("startswith", "password", password, "(self, command)", "authentication"))


def add_player_to_permission_group(self, command):
    player_object = self.bot.players.get(self.player_steamid)
    p = re.search(r"add (.+) to (.+) group", command)
    if p:
        try:
            player_object_to_modify = self.bot.players.get(str(p.group(1)))
            group = str(p.group(2))
            player_object_to_modify.add_permission_level(group)
        except Exception:
            pass

        self.bot.players.upsert(player_object_to_modify, save=True)


actions_authentication.append(("startswith", "add", add_player_to_permission_group, "(self, command)", "authentication"))


def on_player_join(self):
    player_object = self.bot.players.get(self.player_steamid)
    try:
        location = self.bot.locations.get(player_object.steamid, 'spawn')
        self.tn.send_message_to_player(player_object, "Welcome back {} o/".format(player_object.name))
    except KeyError:
        self.tn.send_message_to_player(player_object, "this servers bot says Hi to {} o/".format(player_object.name))
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


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self)", "authentication"))


