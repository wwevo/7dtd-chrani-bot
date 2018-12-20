import re
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def oversized_stack(chrani_bot, source_player, target_player, command):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    try:
        p = re.search(r"has\sstack\sfor\s\"(?P<item_name>.*)\"\sgreater\sthan\sallowed\s\((?P<item_quantity>.*)\)$", command)
        if p:
            response_messages = ResponseMessage()
            message = "Found item-stack of {} that's way too big for player {}".format(p.group("item_quantity"), target_player.name)
            logger.info(message)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['warning'])
            response_messages.add_message(message, True)
            if chrani_bot.tn.kick(target_player, message):
                target_player.blacklisted = True
                message = "kicked player {} for {}".format(target_player.name, message)
                logger.info(message)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['warning'])
            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "has stack for",
        "usage": None
    },
    "action": oversized_stack,
    "group": "hacker",
    "essential": True
})


