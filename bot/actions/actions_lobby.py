import re
from bot.objects.location import Location
from bot.modules.logger import logger
import common


def password(bot, source_player, target_player, command):
    try:
        try:
            location_object = bot.locations.get('system', "lobby")
        except KeyError:
            return False

        p = re.search(r"password\s(\w+)$", command)
        if p:
            pwd = p.group(1)
            if pwd in bot.passwords.values():
                try:
                    location_object = bot.locations.get(target_player.steamid, 'spawn')
                    # if the spawn is enabled, do port the player and disable it.
                    if location_object.enabled is True:
                        if bot.tn.teleportplayer(target_player, location_object=location_object):
                            bot.tn.send_message_to_player(target_player, "You have been ported back to your original spawn!", color=bot.chat_colors['success'])
                            location_object.enabled = False
                            bot.locations.upsert(location_object, save=True)
                        else:
                            bot.tn.send_message_to_player(target_player, "Taking you to your original spawn failed oO!", color=bot.chat_colors['warning'])
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


def set_up_lobby(bot, source_player, target_player, command):
    try:
        location_object = Location()
        location_object.set_owner('system')
        name = 'The Lobby'

        location_object.set_name(name)
        location_object.radius = float(bot.settings.get_setting_by_name("location_default_radius"))
        location_object.warning_boundary = float(bot.settings.get_setting_by_name("location_default_radius")) * float(bot.settings.get_setting_by_name("location_default_warning_boundary_ratio"))

        location_object.set_coordinates(target_player)
        identifier = location_object.set_identifier('lobby')
        location_object.set_description('The \"there is no escape\" Lobby')
        location_object.set_shape("sphere")

        messages_dict = location_object.get_messages_dict()
        messages_dict["entered_locations_core"] = None
        messages_dict["left_locations_core"] = None
        messages_dict["entered_location"] = None
        messages_dict["left_location"] = None
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([target_player.steamid])

        bot.locations.upsert(location_object, save=True)

        bot.tn.send_message_to_player(target_player, "You have set up a lobby", color=bot.chat_colors['success'])
        bot.tn.send_message_to_player(target_player, "Set up the perimeter with {}, while standing on the edge of it.".format(common.find_action_help("lobby", "edit lobby outer perimeter")), color=bot.chat_colors['warning'])
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


def set_up_lobby_outer_perimeter(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get('system', 'lobby')
    except KeyError:
        bot.tn.send_message_to_player(target_player, "you need to set up a lobby first silly: /set up lobby", color=bot.chat_colors['warning'])
        return False

    coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
    distance_to_location = location_object.get_distance(coords)
    set_radius, allowed_range = location_object.set_radius(distance_to_location)
    if set_radius is True:
        bot.tn.send_message_to_player(target_player, "The lobby ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "you given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color=bot.chat_colors['warning'])
        return False

    if location_object.radius <= location_object.warning_boundary:
        set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location - 1)
        if set_radius is True:
            bot.tn.send_message_to_player(target_player, "the inner core has been set to match the outer perimeter.", color=bot.chat_colors['warning'])
        else:
            return False

    bot.locations.upsert(location_object, save=True)


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


def set_up_lobby_inner_perimeter(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get('system', 'lobby')
    except KeyError:
        bot.tn.send_message_to_player(target_player, "you need to set up a lobby first silly: /set up lobby", color=bot.chat_colors['warning'])
        return False

    coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
    distance_to_location = location_object.get_distance(coords)
    set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location)
    if set_radius is True:
        bot.tn.send_message_to_player(target_player, "the lobby ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2)), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "you given range ({}) seems to be invalid ^^".format(int(location_object.warning_boundary * 2)), color=bot.chat_colors['warning'])
        return False

    bot.locations.upsert(location_object, save=True)


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


def goto_lobby(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get('system', 'lobby')
        if bot.tn.teleportplayer(target_player, location_object=location_object):
            bot.tn.send_message_to_player(target_player, "You have ported to the lobby", color=bot.chat_colors['background'])
    except KeyError:
        bot.tn.send_message_to_player(target_player, "There is no lobby :(", color=bot.chat_colors['warning'])


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


def remove_lobby(bot, source_player, target_player, command):
    try:
        bot.locations.remove('system', 'lobby')
    except KeyError:
        bot.tn.send_message_to_player(target_player, "no lobby found oO", color=bot.chat_colors['warning'])
        return False


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


def set_up_lobby_teleport(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get('system', 'lobby')
    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up the lobby first!", color=bot.chat_colors['warning'])
        return False

    if location_object.set_teleport_coordinates(target_player):
        bot.locations.upsert(location_object, save=True)
        bot.tn.send_message_to_player(target_player, "the teleport for {} has been set up!".format('lobby'), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "your position seems to be outside of the location", color=bot.chat_colors['warning'])


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
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
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
