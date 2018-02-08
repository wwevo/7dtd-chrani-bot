import re
from bot.location import Location
from bot.logger import logger

actions_authentication = []


def password(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"password (.+)", command)
        if p:
            pwd = p.group(1)
            if pwd in self.bot.passwords.values():
                if player_object.authenticated is not True:
                    self.tn.say("{} joined the ranks of literate people. Welcome!".format(player_object.name), color=self.bot.chat_colors['background'])
                    self.tn.send_message_to_player(player_object, "Your chat has been enabled!", color=self.bot.chat_colors['success'])

                self.tn.muteplayerchat(player_object, False)
                player_object.set_authenticated(True)
                player_object.add_permission_level("authenticated")

                if pwd == self.bot.passwords['mod']:
                    player_object.add_permission_level("mod")
                    self.tn.send_message_to_player(player_object, "you are a Moderator", color=self.bot.chat_colors['success'])

                if pwd == self.bot.passwords['admin']:
                    player_object.add_permission_level("admin")
                    self.tn.send_message_to_player(player_object, "you are an Admin", color=self.bot.chat_colors['success'])

                if pwd == self.bot.passwords['donator']:
                    player_object.add_permission_level("donator")
                    self.tn.send_message_to_player(player_object, "you are a Donator. Thank you <3", color=self.bot.chat_colors['success'])

            else:
                player_object.set_authenticated(False)
                self.tn.muteplayerchat(player_object, True)
                self.tn.say("{} has entered a wrong password oO!".format(player_object.name), color=self.bot.chat_colors['background'])
                self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
                player_object.remove_permission_level("authenticated")

            self.bot.players.upsert(player_object, save=True)
    except Exception as e:
        logger.error(e)
        pass


actions_authentication.append(("startswith", "password", password, "(self, command)", "authentication"))


def add_player_to_permission_group(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"add player (.+) to (.+) group", command)
        if p:
            steamid_to_modify = str(p.group(1))
            group = str(p.group(2))
            try:
                player_object_to_modify = self.bot.players.get(steamid_to_modify)
                player_object_to_modify.add_permission_level(group)
                self.tn.send_message_to_player(player_object, "{} has been added to the group {}".format(player_object.name, group), color=self.bot.chat_colors['success'])
            except Exception:
                self.tn.send_message_to_player(player_object,"could not find a player with steamid {}".format(steamid_to_modify), color=self.bot.chat_colors['warning'])
                return

            self.bot.players.upsert(player_object_to_modify, save=True)
    except Exception as e:
        logger.error(e)
        pass


actions_authentication.append(("startswith", "add player", add_player_to_permission_group, "(self, command)", "authentication"))


def remove_player_from_permission_group(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"remove player (.+) from (.+) group", command)
        if p:
            steamid_to_modify = str(p.group(1))
            group = str(p.group(2))
            try:
                player_object_to_modify = self.bot.players.get(steamid_to_modify)
                player_object_to_modify.remove_permission_level(group)
                self.tn.send_message_to_player(player_object, "{} has been removed from the group {}".format(player_object.name, group), color=self.bot.chat_colors['success'])
            except Exception:
                self.tn.send_message_to_player(player_object,"could not find a player with steamid {}".format(steamid_to_modify), color=self.bot.chat_colors['warning'])
                return

            self.bot.players.upsert(player_object_to_modify, save=True)
    except Exception as e:
        logger.error(e)
        pass


actions_authentication.append(("startswith", "remove player", remove_player_from_permission_group, "(self, command)", "authentication"))


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location = self.bot.locations.get(player_object.steamid, 'spawn')
            self.tn.send_message_to_player(player_object, "Welcome back {} o/".format(player_object.name), color=self.bot.chat_colors['info'])
        except KeyError:
            self.tn.send_message_to_player(player_object, "this servers bot says Hi to {} o/".format(player_object.name), color=self.bot.chat_colors['info'])
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

        if player_object.has_permission_level("authenticated") is not True:
            self.tn.muteplayerchat(player_object)
            self.tn.send_message_to_player(player_object, "read the rules on https://chrani.net/chrani-bot", color=self.bot.chat_colors['alert'])
        else:
            self.tn.muteplayerchat(player_object, False)
    except Exception as e:
        logger.error(e)
        pass


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self)", "authentication"))
