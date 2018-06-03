import re
from bot.location import Location
from bot.logger import logger

actions_lobby = []


def on_player_join(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
    except Exception as e:
        logger.error(e)
        raise KeyError

    if player_object.has_permission_level("authenticated") is True:
        return False

    if self.tn.muteplayerchat(player_object, True):
        self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])

    return True


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "joined the game",
        "usage" : None
    },
    "action" : on_player_join,
    "env": "(self)",
    "group": "lobby",
    "essential" : True
})


def password(self, command):
    try:
        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"password\s(\w+)$", command)
        if p:
            pwd = p.group(1)
            if pwd in self.bot.passwords.values():
                try:
                    location_object = self.bot.locations.get(player_object.steamid, 'spawn')
                    # if the spawn is enabled, do port the player and disable it.
                    if location_object.enabled is True:
                        self.tn.send_message_to_player(player_object, "You have been ported back to your original spawn!", color=self.bot.chat_colors['success'])
                        if self.tn.teleportplayer(player_object, location_object):
                            location_object.enabled = False
                            self.bot.locations.upsert(location_object, save=True)
                    else:
                        return False
                except KeyError:
                    return False
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "password",
        "usage" : "/password <password>"
    },
    "action" : password,
    "env": "(self)",
    "group": "lobby",
    "essential" : True
})


def set_up_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        location_object = Location()
        location_object.set_owner('system')
        name = 'The Lobby'
        location_object.set_name(name)
        identifier = location_object.set_identifier('lobby')
        location_object.set_description('The \"there is no escape\" Lobby')
        location_object.set_shape("sphere")
        location_object.set_coordinates(player_object)
        # location_object.set_region([player_object.region])
        messages_dict = location_object.get_messages_dict()
        messages_dict["entering_core"] = None
        messages_dict["leaving_core"] = None
        messages_dict["entering_boundary"] = None
        messages_dict["leaving_boundary"] = None
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([player_object.steamid])
        self.bot.locations.upsert(location_object, save=True)
        self.tn.send_message_to_player(player_object, "You have set up a lobby", color=self.bot.chat_colors['success'])
        self.tn.send_message_to_player(player_object, "Set up the perimeter with /set lobby outer perimeter, while standing on the edge of it.".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "add lobby",
        "usage" : "/add lobby"
    },
    "action" : set_up_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})


def set_up_lobby_outer_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_radius(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "Your given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit lobby outer perimeter",
        "usage" : "/edit lobby outer perimeter"
    },
    "action" : set_up_lobby_outer_perimeter,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})


def set_up_lobby_inner_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_warning_boundary(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "The lobby-warnings will be issued from this point on", color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "Is this inside the lobby perimeter?", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit lobby inner perimeter",
        "usage" : "/edit lobby inner perimeter"
    },
    "action" : set_up_lobby_inner_perimeter,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})


def goto_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
            self.tn.send_message_to_player(player_object, "You have ported to the lobby", color=self.bot.chat_colors['background'])
            self.tn.teleportplayer(player_object, location_object)
        except KeyError:
            self.tn.send_message_to_player(player_object, "There is no lobby :(", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "goto lobby",
        "usage" : "/goto lobby"
    },
    "action" : goto_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})


def remove_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            self.bot.locations.remove('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "no lobby found oO", color=self.bot.chat_colors['warning'])
            return False
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "remove lobby",
        "usage" : "/remove lobby"
    },
    "action" : remove_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})


def set_up_lobby_teleport(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up the lobby first!", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_teleport_coordinates(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "the teleport for {} has been set up!".format('lobby'), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "your position seems to be outside of the location", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_lobby.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit lobby teleport",
        "usage" : "/edit lobby teleport"
    },
    "action" : set_up_lobby_teleport,
    "env": "(self)",
    "group": "lobby",
    "essential" : False
})
"""
here come the observers
"""
observers_lobby = []


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        if player_object.authenticated is not True:
            if not location_object.player_is_inside_boundary(player_object):
                if self.tn.teleportplayer(player_object, location_object):
                    player_object.set_coordinates(location_object)
                    self.bot.players.upsert(player_object)
                    logger.info("{} has been ported to the lobby!".format(player_object.name))
                    self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>", color=self.bot.chat_colors['alert'])
                    self.tn.send_message_to_player(player_object, "see https://chrani.net/chrani-bot for more information!", color=self.bot.chat_colors['warning'])
                    if self.tn.muteplayerchat(player_object, True):
                        self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


observers_lobby.append(("monitor", "player left lobby", player_is_outside_boundary, "(self)"))
