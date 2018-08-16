import re
from bot.objects.location import Location
from bot.modules.logger import logger
import common


def check_building_site(bot, source_player, target_player, command):
    try:
        bases_near_list, landclaims_near_list = bot.check_for_homes(target_player)

        if not bases_near_list and not landclaims_near_list:
            bot.tn.send_message_to_player(target_player, "Nothing near or far. Feel free to build here".format(len(bases_near_list), len(landclaims_near_list)), color=bot.chat_colors['success'])
        else:
            bot.tn.send_message_to_player(target_player, "bases near: {}, landclaims near: {}".format(len(bases_near_list), len(landclaims_near_list)), color=bot.chat_colors['warning'])

    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "can i build here",
        "usage": "/can i build here"
    },
    "action": check_building_site,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home(bot, source_player, target_player, command):
    try:
        bases_near_list, landclaims_near_list = bot.check_for_homes(target_player)

        if bases_near_list or landclaims_near_list:
            bot.tn.send_message_to_player(target_player, "Can not set up a home here. Other bases are too close!", color=bot.chat_colors['error'])
            return False

        location_object = Location()
        location_object.set_owner(target_player.steamid)
        name = 'My Home'

        location_object.set_name(name)
        location_object.radius = float(bot.settings.get_setting_by_name("location_default_radius"))
        location_object.warning_boundary =float(bot.settings.get_setting_by_name("location_default_radius")) * float(bot.settings.get_setting_by_name("location_default_warning_boundary_ratio"))

        location_object.set_coordinates(target_player)
        identifier = location_object.set_identifier('home')

        location_object.set_description("{}\'s home".format(target_player.name))
        location_object.set_shape("sphere")

        messages_dict = location_object.get_messages_dict()
        messages_dict["entered_locations_core"] = None
        messages_dict["left_locations_core"] = None
        messages_dict["entered_location"] = "you have entered {}\'s estate".format(target_player.name)
        messages_dict["left_location"] = "you have left {}\'s estate".format(target_player.name)
        location_object.set_messages(messages_dict)
        location_object.set_list_of_players_inside([target_player.steamid])

        bot.locations.upsert(location_object, save=True)

        bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
        bot.tn.say("{} has decided to settle down!".format(target_player.name), color=bot.chat_colors['background'])
        bot.tn.send_message_to_player(target_player, "Home is where your hat is!", color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "add home",
        "usage": "/add home"
    },
    "action": set_up_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def remove_home(bot, source_player, target_player, command):
    try:
        bot.locations.remove(target_player.steamid, 'home')

    except KeyError:
        bot.tn.send_message_to_player(target_player, "I could not find your home. Did you set one up?", color=bot.chat_colors['warning'])
        raise KeyError

    bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
    bot.tn.send_message_to_player(target_player, "Your home has been removed.", color=bot.chat_colors['warning'])

    return True


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "remove home",
        "usage": "/remove home"
    },
    "action": remove_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_teleport(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")

    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up a home first!", color=bot.chat_colors['warning'])
        return False

    if location_object.set_teleport_coordinates(target_player):
        bot.locations.upsert(location_object, save=True)
        bot.tn.send_message_to_player(target_player, "your teleport has been set up!", color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "your position seems to be outside your home", color=bot.chat_colors['warning'])


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit home teleport",
        "usage": "/edit home teleport"
    },
    "action": set_up_home_teleport,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def protect_inner_core(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")

    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up a home first!", color=bot.chat_colors['warning'])
        return False

    if location_object.set_protected_core(True):
        bot.locations.upsert(location_object, save=True)
        bot.tn.send_message_to_player(target_player, "your home is now protected!", color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "something went wrong :(", color=bot.chat_colors['warning'])



common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "enable home protection",
        "usage": "/enable home protection"
    },
    "action": protect_inner_core,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def unprotect_inner_core(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")

    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up a home first!", color=bot.chat_colors['warning'])
        return False

    if location_object.set_protected_core(False):
        bot.locations.upsert(location_object, save=True)
        bot.tn.send_message_to_player(target_player, "your home is now unprotected!", color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "something went wrong :(", color=bot.chat_colors['warning'])


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "disable home protection",
        "usage": "/disable home protection"
    },
    "action": unprotect_inner_core,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_name(bot, source_player, target_player, command):
    p = re.search(r"edit\shome\sname\s([\W\w\s]{1,19})$", command)
    if p:
        description = p.group(1)
        try:
            location_object = bot.locations.get(target_player.steamid, "home")
        except KeyError:
            bot.tn.send_message_to_player(target_player, "{} can not name that which you do not have!".format(target_player.name), color=bot.chat_colors['warning'])
            raise KeyError

    location_object.set_description(description)
    messages_dict = {
        "left_locations_core": "you are leaving {}\'s core".format(description),
        "left_location": "you are leaving {}".format(description),
        "entered_location": "you are entering {}".format(description),
        "entered_locations_core": "you are entering {}\'s core".format(description)
    }
    location_object.set_messages(messages_dict)
    bot.locations.upsert(location_object, save=True)
    bot.socketio.emit('refresh_locations', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
    bot.tn.send_message_to_player(target_player, "Your home is called {} now \o/".format(location_object.description), color=bot.chat_colors['background'])

    return True


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "edit home name",
        "usage": "/edit home name <name>"
    },
    "action": set_up_home_name,
    "env": "(self, command)",
    "group": "home",
    "essential": False
})


def take_me_home(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")
        if location_object.player_is_inside_boundary(target_player):
            bot.tn.send_message_to_player(target_player, "eh, you already ARE home oO".format(target_player.name), color=bot.chat_colors['warning'])
        else:
            bot.tn.teleportplayer(target_player, location_object=location_object)
            bot.tn.send_message_to_player(target_player, "you have ported home!".format(target_player.name), color=bot.chat_colors['success'])
    except KeyError:
        bot.tn.send_message_to_player(target_player, "You seem to be homeless".format(target_player.name), color=bot.chat_colors['warning'])


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "take me home",
        "usage": "/take me home"
    },
    "action": take_me_home,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def goto_player_home(bot, source_player, target_player, command):
    p = re.search(r"take\sme\sto\splayer\s((?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+))\shome", command)
    if p:
        player_steamid = p.group("steamid")
        player_entityid = p.group("entityid")
        if player_steamid is None:
            player_steamid = bot.players.entityid_to_steamid(player_entityid)
            if player_steamid is False:
                raise KeyError
        try:
            player_object_to_port_to = bot.players.load(player_steamid)
            location_object = bot.locations.get(player_object_to_port_to.steamid, "home")
            bot.tn.teleportplayer(target_player, location_object=location_object)
            bot.tn.send_message_to_player(target_player, "You went to visit {}'s home".format(player_object_to_port_to.name), color=bot.chat_colors['background'])
            bot.tn.send_message_to_player(player_object_to_port_to, "{} went to visit your home!".format(target_player.name), color=bot.chat_colors['warning'])
        except KeyError:
            bot.tn.send_message_to_player(target_player, "Could not find {}'s home".format(player_steamid), color=bot.chat_colors['warning'])
            pass


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "take me to player",
        "usage": "/take me to player <steamid/entityid> home"
    },
    "action": goto_player_home,
    "env": "(self, command)",
    "group": "home",
    "essential": False
})


def set_up_home_outer_perimeter(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")
    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up a home first!", color=bot.chat_colors['warning'])
        return False

    coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
    distance_to_location = location_object.get_distance(coords)
    set_radius, allowed_range = location_object.set_radius(distance_to_location)
    if set_radius is True:
        bot.locations.upsert(location_object)
        bot.tn.send_message_to_player(target_player, "your estate ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=bot.chat_colors['success'])
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
        "trigger": "edit home outer perimeter",
        "usage": "/edit home outer perimeter"
    },
    "action": set_up_home_outer_perimeter,
    "env": "(self)",
    "group": "home",
    "essential": False
})


def set_up_home_inner_perimeter(bot, source_player, target_player, command):
    try:
        location_object = bot.locations.get(target_player.steamid, "home")
    except KeyError:
        bot.tn.send_message_to_player(target_player, "coming from the wrong end... set up a home first!", color=bot.chat_colors['warning'])
        return False

    coords = (target_player.pos_x, target_player.pos_y, target_player.pos_z)
    distance_to_location = location_object.get_distance(coords)
    set_radius, allowed_range = location_object.set_warning_boundary(distance_to_location)
    if set_radius is True:
        bot.tn.send_message_to_player(target_player, "your private area ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2)), color=bot.chat_colors['success'])
    else:
        bot.tn.send_message_to_player(target_player, "you given range ({}) seems to be invalid. Are you inside your home area?".format(int(location_object.warning_boundary * 2)), color=bot.chat_colors['warning'])
        return False

    bot.locations.upsert(location_object, save=True)


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "edit home inner perimeter",
        "usage": "/edit home inner perimeter"
    },
    "action": set_up_home_inner_perimeter,
    "env": "(self)",
    "group": "home",
    "essential": False
})


