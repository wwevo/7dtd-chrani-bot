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
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "brokenLeg")
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "sprainedLeg")
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "buffLegBroken")
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "buffLegSprained")
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
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "bleeding")
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "debuffplayer", target_player, "buffInternalBleeding")

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
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "buffplayer", target_player, "firstAidLarge")
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
    "group": "testing",
    "essential": False
})
