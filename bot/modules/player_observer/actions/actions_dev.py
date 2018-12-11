import re
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common


def fix_players_legs(chrani_bot, source_player, target_player, command):
    """Fixes the legs of the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /fix my legs please

    example:
    /fix my legs please

    notes:
    does not check if the player is injured at all
    """
    try:
        response_messages = ResponseMessage()
        chrani_bot.tn.debuffplayer(target_player, "brokenLeg")
        chrani_bot.tn.debuffplayer(target_player, "sprainedLeg")
        message = "your legs have been taken care of ^^"
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "fix my legs please",
        "usage": "/fix my legs please"
    },
    "action": fix_players_legs,
    "env": "(self)",
    "group": "testing",
    "essential": False
})


def stop_the_bleeding(chrani_bot, source_player, target_player, command):
    """Removes the 'bleeding' buff from the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /make me stop leaking

    example:
    /make me stop leaking

    notes:
    does not check if the player is injured at all
    """
    try:
        response_messages = ResponseMessage()
        chrani_bot.tn.debuffplayer(target_player, "bleeding")
        message = "your wounds have been bandaided ^^"
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "make me stop leaking",
        "usage": "/make me stop leaking"
    },
    "action": stop_the_bleeding,
    "env": "(self)",
    "group": "testing",
    "essential": False
})


def apply_first_aid(chrani_bot, source_player, target_player, command):
    """Applies the 'firstAidLarge' buff to the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /heal me up scotty

    example:
    /heal me up scotty

    notes:
    does not check if the player is injured at all
    """
    try:
        response_messages = ResponseMessage()
        chrani_bot.tn.buffplayer(target_player, "firstAidLarge")
        message = "feel the power flowing through you!! ^^"
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
        response_messages.add_message(message, True)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "heal me up scotty",
        "usage": "/heal me up scotty"
    },
    "action": apply_first_aid,
    "env": "(self)",
    "group": "testing",
    "essential": False
})


def remove_entity(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\sentity\s(?P<entity_id>[0-9]+)$", command)
        if p:
            response_messages = ResponseMessage()
            entity_id = p.group("entity_id")
            if chrani_bot.tn.remove_entity(entity_id):
                message = "shunned screamer ({}) from village ^^".format(entity_id)
                response_messages.add_message(message, True)
            else:
                message = "removal of screamer ({}) failed :/".format(entity_id)
                response_messages.add_message(message, False)

            logger.info(message)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['standard'])

            return response_messages

        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "remove entity",
        "usage": None
    },
    "action": remove_entity,
    "env": "(self)",
    "group": "testing",
    "essential": False
})


def supply_crate_spawned(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"an\sairdrop\shas\sarrived\s@\s\((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\)$", command)
        if p:
            response_messages = ResponseMessage()
            pos_x = p.group("pos_x")
            pos_y = p.group("pos_y")
            pos_z = p.group("pos_z")
            message = "supply crate at position ([ffffff]{pos_x}[-] [ffffff]{pos_y}[-] [ffffff]{pos_z}[-])".format(pos_x=pos_x, pos_y=pos_y, pos_z=pos_z)

            logger.info(message)
            online_players = chrani_bot.players.get_all_players(get_online_only=True)
            for player in online_players:
                if any(x in ["donator", "mod", "admin"] for x in player.permission_levels):
                    chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player, message, chrani_bot.chat_colors['success'])

            return response_messages

        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "an airdrop has arrived @",
        "usage": None
    },
    "action": supply_crate_spawned,
    "env": "(self)",
    "group": "testing",
    "essential": False
})


def skip_bloodmoon(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        if chrani_bot.current_gametime is not None and chrani_bot.ongoing_bloodmoon():
            day_after_horde = None
            if chrani_bot.is_it_horde_day(chrani_bot.current_gametime["day"]):
                day_after_horde = int(chrani_bot.current_gametime["day"]) + 1
            elif chrani_bot.is_it_horde_day(int(chrani_bot.current_gametime["day"]) - 1):
                day_after_horde = int(chrani_bot.current_gametime["day"])

            if day_after_horde is not None:
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "settime", "{day} {hour} {minute}".format(day=day_after_horde, hour=4, minute=0))
                message = "bloodmoon got skipped by {}".format(source_player.name)
                response_messages.add_message(message, True)
            else:
                message = "skipping bloodmoon failed :(".format(source_player.name)
                response_messages.add_message(message, False)

            logger.info(message)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['warning'])
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "skip bloodmoon",
        "usage": "/skip bloodmoon"
    },
    "action": skip_bloodmoon,
    "env": "(self)",
    "group": "testing",
    "essential": False
})
