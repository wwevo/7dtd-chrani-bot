import re
from bot.assorted_functions import ResponseMessage
from bot.modules.logger import logger
import common


def fix_players_legs(bot, source_player, target_player, command):
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
        bot.tn.debuffplayer(target_player, "brokenLeg")
        bot.tn.debuffplayer(target_player, "sprainedLeg")
        message = "your legs have been taken care of ^^"
        bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
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


def stop_the_bleeding(bot, source_player, target_player, command):
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
        bot.tn.debuffplayer(target_player, "bleeding")
        message = "your wounds have been bandaided ^^"
        bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
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


def apply_first_aid(bot, source_player, target_player, command):
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
        bot.tn.buffplayer(target_player, "firstAidLarge")
        message = "feel the power flowing through you!! ^^"
        bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
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


def remove_entity(bot, source_player, target_player, command):
    try:
        p = re.search(r"screamer\sspawned\sinside\svillage\s(?P<entity_id>[0-9]+)$", command)
        if p:
            response_messages = ResponseMessage()
            entity_id = p.group("entity_id")
            if bot.tn.remove_entity(entity_id):
                message = "shunned screamer ({}) from village ^^".format(entity_id)
                response_messages.add_message(message, True)
            else:
                message = "removal of screamer ({}) failed :/".format(entity_id)
                response_messages.add_message(message, False)

            logger.info(message)
            bot.tn.say(message, color=bot.chat_colors['background'])

            return response_messages

        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "screamer spawned inside village",
        "usage": None
    },
    "action": remove_entity,
    "env": "(self)",
    "group": "testing",
    "essential": False
})
