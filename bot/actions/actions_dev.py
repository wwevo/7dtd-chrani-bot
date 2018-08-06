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
        bot.tn.debuffplayer(target_player, "brokenLeg")
        bot.tn.debuffplayer(target_player, "sprainedLeg")
        bot.tn.send_message_to_player(target_player, "your legs have been taken care of ^^", color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


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
        bot.tn.debuffplayer(target_player, "bleeding")
        bot.tn.send_message_to_player(target_player, "your wounds have been bandaided ^^", color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


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
        bot.tn.buffplayer(target_player, "firstAidLarge")
        bot.tn.send_message_to_player(target_player, "feel the power flowing through you!! ^^", color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


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
