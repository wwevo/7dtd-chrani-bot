from bot.modules.logger import logger
import common


def reload_from_db(bot, source_player, target_player, command):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    try:
        bot.load_from_db()
        bot.tn.send_message_to_player(target_player, "loaded all from storage!", color=bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "reinitialize",
        "usage": "/reinitialize"
    },
    "action": reload_from_db,
    "env": "(self)",
    "group": "system",
    "essential": False
})


def shutdown_bot(bot, source_player, target_player, command):
    """Shuts down the bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /shut down the matrix

    example:
    /shut down the matrix

    notes:
    Together with a cronjob starting the bot every minute, this can be
    used for restarting it from within the game
    """
    try:
        bot.shutdown()
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "shut down the matrix",
        "usage": "/shut down the matrix"
    },
    "action": shutdown_bot,
    "env": "(self)",
    "group": "system",
    "essential": False
})


def pause_bot(bot, source_player, target_player, command):
    """Pauses the bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /pause bot

    example:
    /pause bot

    """
    try:
        bot.is_paused = True
        bot.tn.say("bot operations have been suspended", color=bot.chat_colors['background'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "pause bot",
        "usage": "/pause bot"
    },
    "action": pause_bot,
    "env": "(self)",
    "group": "system",
    "essential": False
})


def resume_bot(bot, source_player, target_player, command):
    """Resumes paused bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /resume bot

    example:
    /resume bot

    """
    try:
        bot.is_paused = False
        bot.tn.say("bot operations have been resumed", color=bot.chat_colors['background'])
    except Exception as e:
        logger.exception(e)
        pass


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "resume bot",
        "usage": "/resume bot"
    },
    "action": resume_bot,
    "env": "(self)",
    "group": "system",
    "essential": False
})

