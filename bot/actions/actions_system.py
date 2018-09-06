import re
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def reload_from_db(bot, source_player, target_player, command):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    response_messages = ResponseMessage()
    try:
        bot.load_from_db()
        message = "loaded all data from storage."
        bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['success'])
        response_messages.add_message(message, True)
        bot.socketio.emit('reinitialize', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
    except Exception as e:
        message = "loading data from storage failed."
        bot.tn.send_message_to_player(target_player, message, color=bot.chat_colors['warning'])
        response_messages.add_message(message, False)
        logger.exception(e)
        pass

    return response_messages


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
    p = re.search(r"shut\sdown\sthe\smatrix$", command)
    if p:
        response_messages = ResponseMessage()
        try:
            message = "The bot is about to shut down..."
            response_messages.add_message(message, True)
            bot.tn.say(message, color=bot.chat_colors['background'])
            bot.initiate_shutdown = True
        except Exception as e:
            logger.exception(e)
            pass

        return ResponseMessage()
    else:
        raise ValueError("action does not fully match the trigger-string")


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
    response_messages = ResponseMessage()
    try:
        bot.is_paused = True
        bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
        message = "The bot operations have been suspended"
        response_messages.add_message(message, True)
        bot.tn.say(message, color=bot.chat_colors['success'])
    except Exception as e:
        message = "Pausing of the bot failed."
        response_messages.add_message(message, False)
        bot.tn.say(message, color=bot.chat_colors['warning'])
        logger.exception(e)
        pass

    return response_messages


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
    response_messages = ResponseMessage()
    try:
        bot.is_paused = False
        bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
        message = "The bots operations have been resumed"
        response_messages.add_message(message, True)
        bot.tn.say(message, color=bot.chat_colors['success'])
    except Exception as e:
        message = "Resuming of the bot failed."
        response_messages.add_message(message, False)
        bot.tn.say(message, color=bot.chat_colors['warning'])
        logger.exception(e)
        pass

    return response_messages


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


def shutdown_server(bot, source_player, target_player, command):
    p = re.search(r"shut\sdown\sthe\sworld$", command)
    if p:
        response_messages = ResponseMessage()
        try:
            message = "The server is about to shut down..."
            response_messages.add_message(message, True)
            bot.tn.say(message, color=bot.chat_colors['background'])
            bot.tn.shutdown()
        except Exception as e:
            logger.exception(e)

        return ResponseMessage()
    else:
        raise ValueError("action does not fully match the trigger-string")


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "shut down the world",
        "usage": "/shut down the world"
    },
    "action": shutdown_server,
    "env": "(self)",
    "group": "system",
    "essential": False
})


