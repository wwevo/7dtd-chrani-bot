import re
from bot.objects.location import Location
from bot.modules.logger import logger
import common


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
                        if self.tn.teleportplayer(player_object, location_object=location_object):
                            self.tn.send_message_to_player(player_object, "You have been ported back to your original spawn!", color=self.bot.chat_colors['success'])
                            location_object.enabled = False
                            self.bot.locations.upsert(location_object, save=True)
                        else:
                            self.tn.send_message_to_player(player_object, "Taking you to your original spawn failed oO!", color=self.bot.chat_colors['warning'])
                    else:
                        return False
                except KeyError:
                    return False
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "password",
        "usage": "/password <password>"
    },
    "action": password,
    "env": "(self)",
    "group": "lobby",
    "essential": True
})


def set_up_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)

        location_object = Location()
        location_object.set_owner('system')
        name = 'The Lobby'

        location_object.set_name(name)
        location_object.radius = float(self.bot.settings.get_setting_by_name("location_default_radius"))
        location_object.warning_boundary = float(self.bot.settings.get_setting_by_name("location_default_radius")) * float(self.bot.settings.get_setting_by_name("location_default_warning_boundary_ratio"))

        location_object.set_coordinates(player_object)
        identifier = location_object.set_identifier('lobby')
        location_object.set_description('The \"there is no escape\" Lobby')
        location_object.set_shape("sphere")

        messages_dict = location_object.get_messages_dict()
        messages_dict["entered_locations_core"] = None
        messages_dict["left_locations_core"] = None
        messages_dict["entered_location"] = None
        messages_dict["left_location"] = None
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([player_object.steamid])

        self.bot.locations.upsert(location_object, save=True)

        self.tn.send_message_to_player(player_object, "You have set up a lobby", color=self.bot.chat_colors['success'])
        self.tn.send_message_to_player(player_object, "Set up the perimeter with {}, while standing on the edge of it.".format(common.find_action_help("lobby", "edit lobby outer perimeter")), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "add lobby",
        "usage": "/add lobby"
    },
    "action": set_up_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential": False
})


def set_up_lobby_outer_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)
        distance_to_location = location_object.get_distance(coords)
        set_radius, allowed_range = location_object.set_radius(distance_to_location)
        if set_radius is True:
            self.tn.send_message_to_player(player_object, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['warning'])
            return False

        if location_object.radius <= location_object.warning_boundary:
            set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
            if set_radius is True:
                self.tn.send_message_to_player(player_object, "the inner core has been set to match the outer perimeter.", color=self.bot.chat_colors['warning'])
            else:
                return False

        self.bot.locations.upsert(location_object, save=True)
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby outer perimeter",
        "usage": "/edit lobby outer perimeter"
    },
    "action": set_up_lobby_outer_perimeter,
    "env": "(self)",
    "group": "lobby",
    "essential": False
})


def set_up_lobby_inner_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
        except KeyError:
            self.tn.send_message_to_player(player_object, "you need to set up a lobby first silly: /set up lobby", color=self.bot.chat_colors['warning'])
            return False

        coords = (player_object.pos_x, player_object.pos_y, player_object.pos_z)
        distance_to_location = location_object.get_distance(coords)
        set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location)
        if set_radius is True:
            self.tn.send_message_to_player(player_object, "the lobby ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['warning'])
            return False

        self.bot.locations.upsert(location_object, save=True)
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby inner perimeter",
        "usage": "/edit lobby inner perimeter"
    },
    "action": set_up_lobby_inner_perimeter,
    "env": "(self)",
    "group": "lobby",
    "essential": False
})


def goto_lobby(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get('system', 'lobby')
            if self.tn.teleportplayer(player_object, location_object=location_object):
                self.tn.send_message_to_player(player_object, "You have ported to the lobby", color=self.bot.chat_colors['background'])
        except KeyError:
            self.tn.send_message_to_player(player_object, "There is no lobby :(", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "goto lobby",
        "usage": "/goto lobby"
    },
    "action": goto_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential": False
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
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "remove lobby",
        "usage": "/remove lobby"
    },
    "action": remove_lobby,
    "env": "(self)",
    "group": "lobby",
    "essential": False
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
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit lobby teleport",
        "usage": "/edit lobby teleport"
    },
    "action": set_up_lobby_teleport,
    "env": "(self)",
    "group": "lobby",
    "essential": False
})
"""
here come the observers
"""


# the only lobby specific observer. since it is a location, generic observers can be found in actions_locations
def player_is_outside_boundary(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        if player_object.authenticated is True:
            return

        try:
            location_object = self.bot.locations.get('system', "lobby")
        except KeyError:
            return False

        if location_object.enabled is True and not location_object.player_is_inside_boundary(player_object):
            if self.tn.teleportplayer(player_object, location_object=location_object):
                player_object.set_coordinates(location_object)
                self.bot.players.upsert(player_object)
                logger.info("{} has been ported to the lobby!".format(player_object.name))
                self.tn.send_message_to_player(player_object, "You have been ported to the lobby! Authenticate with /password <password>", color=self.bot.chat_colors['alert'])
                self.tn.send_message_to_player(player_object, "see https://chrani.net/chrani-bot for more information!", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "player left lobby",
    "action": player_is_outside_boundary,
    "env": "(self)",
    "essential": True
})
