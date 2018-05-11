import re
from bot.logger import logger

actions_authentication = []


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    if player_object.has_permission_level("authenticated") is not True:
        self.tn.send_message_to_player(player_object, "read the rules on https://chrani.net/chrani-bot", color=self.bot.chat_colors['warning'])
        self.tn.send_message_to_player(player_object, "this is a development server. you can play here, but there's no support or anything really.", color=self.bot.chat_colors['info'])
        self.tn.send_message_to_player(player_object, "Enjoy!", color=self.bot.chat_colors['info'])
        return False

    return True


actions_authentication.append(("isequal", "joined the game", on_player_join, "(self)", "authentication", True))


def password(self, command):
    """Adds player to permission-group(s) according to the password entered

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /password <password>

    example:
    /password openup
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    p = re.search(r"password\s(?P<password>\w+)$", command)
    try:
        pwd = p.group("password")
    except (AttributeError, IndexError) as e:
        return False

    if pwd not in self.bot.passwords.values() and player_object.authenticated is not True :
        self.tn.send_message_to_player(player_object, "You have entered a wrong password!", color=self.bot.chat_colors['warning'])
        return False
    elif pwd not in self.bot.passwords.values() and player_object.authenticated is True:
        player_object.set_authenticated(False)
        player_object.remove_permission_level("authenticated")
        self.tn.send_message_to_player(player_object, "You have lost your authentication!", color=self.bot.chat_colors['warning'])
        if self.tn.muteplayerchat(player_object, True):
            self.tn.send_message_to_player(player_object, "Your chat has been disabled!",color=self.bot.chat_colors['warning'])

        self.bot.players.upsert(player_object, save=True)
        return False

    player_object.set_authenticated(True)
    player_object.add_permission_level("authenticated")
    self.tn.say("{} joined the ranks of literate people. Welcome!".format(player_object.name), color=self.bot.chat_colors['background'])
    if self.tn.muteplayerchat(player_object, False):
        self.tn.send_message_to_player(player_object, "Your chat has been enabled!", color=self.bot.chat_colors['success'])

    """ makeshift promotion system """
    # TODO: well, this action should only care about general authentication. things like admin and mod should be handled somewhere else really
    if pwd == self.bot.passwords['admin']:
        player_object.add_permission_level("admin")
        self.tn.send_message_to_player(player_object, "you are an Admin", color=self.bot.chat_colors['success'])
    elif pwd == self.bot.passwords['mod']:
        player_object.add_permission_level("mod")
        self.tn.send_message_to_player(player_object, "you are a Moderator", color=self.bot.chat_colors['success'])
    elif pwd == self.bot.passwords['donator']:
        player_object.add_permission_level("donator")
        self.tn.send_message_to_player(player_object, "you are a Donator. Thank you <3", color=self.bot.chat_colors['success'])

    self.bot.players.upsert(player_object, save=True)
    return True


actions_authentication.append(("startswith", "password", password, "(self, command)", "authentication", True))


def add_player_to_permission_group(self, command):
    """Adds player to permission-group

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /add player <steamid/entityid> to group <group_name>

    example:
    /add player 76561198040658370 to group admin
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    p = re.search(r"add\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sto\sgroup\s(?P<group_name>\w+)$", command)
    if p:
        steamid_to_modify = p.group("steamid")
        entityid_to_modify = p.group("entityid")
        if steamid_to_modify is None:
            steamid_to_modify = self.bot.players.entityid_to_steamid(entityid_to_modify)
            if steamid_to_modify is False:
                raise KeyError

        group = str(p.group("group_name"))
        if group not in self.bot.permission_levels_list:
            self.tn.send_message_to_player(player_object, "the group {} does not exist!".format(group), color=self.bot.chat_colors['success'])
            return False

        try:
            player_object_to_modify = self.bot.players.get(steamid_to_modify)
            player_object_to_modify.add_permission_level(group)
            self.tn.send_message_to_player(player_object, "{} has been added to the group {}".format(player_object.name, group), color=self.bot.chat_colors['success'])
        except Exception:
            self.tn.send_message_to_player(player_object,"could not find a player with steamid {}".format(steamid_to_modify), color=self.bot.chat_colors['warning'])
            return

        self.bot.players.upsert(player_object_to_modify, save=True)


actions_authentication.append(("startswith", "add player", add_player_to_permission_group, "(self, command)", "authentication"))


def remove_player_from_permission_group(self, command):
    """Removes player from permission-group

    Keyword arguments:
    self -- the bot
    command -- the entire chatline (bot command)

    expected bot command:
    /remove player <steamid/entityid> from group <group_name>

    example:
    /remove player 76561198040658370 from group admin
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    p = re.search(r"remove\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\sfrom\sgroup\s(?P<group_name>\w+)$", command)
    if p:
        steamid_to_modify = p.group("steamid")
        entityid_to_modify = p.group("entityid")
        if steamid_to_modify is None:
            steamid_to_modify = self.bot.players.entityid_to_steamid(entityid_to_modify)
            if steamid_to_modify is False:
                raise KeyError

        group = str(p.group("group_name"))
        if group not in self.bot.permission_levels_list:
            self.tn.send_message_to_player(player_object, "the group {} does not exist!".format(group), color=self.bot.chat_colors['success'])
            return False

        try:
            player_object_to_modify = self.bot.players.get(steamid_to_modify)
            player_object_to_modify.remove_permission_level(group)
            self.tn.send_message_to_player(player_object, "{} has been removed from the group {}".format(player_object.name, group), color=self.bot.chat_colors['success'])
        except Exception:
            self.tn.send_message_to_player(player_object,"could not find a player with steamid {}".format(steamid_to_modify), color=self.bot.chat_colors['warning'])
            return

        self.bot.players.upsert(player_object_to_modify, save=True)


actions_authentication.append(("startswith", "remove player", remove_player_from_permission_group, "(self, command)", "authentication"))
