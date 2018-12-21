import re
from bot.modules.logger import logger
import common
from bot.assorted_functions import ResponseMessage


def reload_from_db(chrani_bot, source_player, target_player, command):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    try:
        response_messages = ResponseMessage()
        try:
            chrani_bot.load_from_db()
            message = "loaded all data from storage."
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['success'])
            response_messages.add_message(message, True)
            chrani_bot.socketio.emit('reinitialize', {"steamid": target_player.steamid, "entityid": target_player.entityid}, namespace='/chrani-bot/public')
        except Exception as e:
            message = "loading data from storage failed."
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", target_player, message, chrani_bot.chat_colors['warning'])
            response_messages.add_message(message, False)
            logger.debug(e)
            pass

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "reinitialize",
        "usage": "/reinitialize"
    },
    "action": reload_from_db,
    "group": "system",
    "essential": False
})


def shutdown_bot(chrani_bot, source_player, target_player, command):
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
        p = re.search(r"shut\sdown\sthe\smatrix$", command)
        if p:
            response_messages = ResponseMessage()
            try:
                message = "The bot is about to shut down..."
                response_messages.add_message(message, True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['standard'])
                chrani_bot.initiate_shutdown = True
            except Exception as e:
                logger.debug(e)
                pass

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "shut down the matrix",
        "usage": "/shut down the matrix"
    },
    "action": shutdown_bot,
    "group": "system",
    "essential": False
})


def pause_bot(chrani_bot, source_player, target_player, command):
    """Pauses the bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /pause bot

    example:
    /pause bot

    """
    try:
        response_messages = ResponseMessage()
        try:
            chrani_bot.is_paused = True
            chrani_bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
            message = "The bot operations have been suspended"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['success'])
        except Exception as e:
            message = "Pausing of the bot failed."
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['warning'])
            logger.debug(e)
            pass

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "pause bot",
        "usage": "/pause bot"
    },
    "action": pause_bot,
    "group": "system",
    "essential": False
})


def resume_bot(chrani_bot, source_player, target_player, command):
    """Resumes paused bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /resume bot

    example:
    /resume bot

    """
    try:
        response_messages = ResponseMessage()
        try:
            chrani_bot.is_paused = False
            chrani_bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
            message = "The bots operations have been resumed"
            response_messages.add_message(message, True)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['success'])
        except Exception as e:
            message = "Resuming of the bot failed."
            response_messages.add_message(message, False)
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['warning'])
            logger.debug(e)
            pass

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "resume bot",
        "usage": "/resume bot"
    },
    "action": resume_bot,
    "group": "system",
    "essential": False
})


def shutdown_server(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"shut\sdown\sthe\sworld$", command)
        if p:
            response_messages = ResponseMessage()
            try:
                message = "The server is about to shut down..."
                response_messages.add_message(message, True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.chat_colors['standard'])
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "shutdown")
            except Exception as e:
                logger.debug(e)

            return response_messages
        else:
            raise ValueError("action does not fully match the trigger-string")

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "shut down the world",
        "usage": "/shut down the world"
    },
    "action": shutdown_server,
    "group": "system",
    "essential": False
})


def disable_scheduler(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"disable\sscheduler\s(?P<scheduler>(\S+))$", command)
        if p:
            scheduler_name = p.group("scheduler")
            chrani_bot.socketio.emit('refresh_scheduler_status', {"scheduler_name": scheduler_name}, namespace='/chrani-bot/public')
            chrani_bot.schedulers_controller[scheduler_name]["is_active"] = False
            response_messages.add_message("scheduler {} disabled".format(scheduler_name), True)
        else:
            response_messages.add_message("disabling scheduler failed", False)
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "disable scheduler ",
        "usage": "/disable scheduler <name>"
    },
    "action": disable_scheduler,
    "group": "system",
    "essential": False
})


def enable_scheduler(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"enable\sscheduler\s(?P<scheduler>(\S+))$", command)
        if p:
            scheduler_name = p.group("scheduler")
            chrani_bot.socketio.emit('refresh_scheduler_status', {"scheduler_name": scheduler_name}, namespace='/chrani-bot/public')
            chrani_bot.schedulers_controller[scheduler_name]["is_active"] = True
            response_messages.add_message("scheduler {} enabled".format(scheduler_name), True)
        else:
            response_messages.add_message("enabling scheduler failed", False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "enable scheduler ",
        "usage": "/enable scheduler <name>"
    },
    "action": enable_scheduler,
    "group": "system",
    "essential": False
})


def disable_player_observer(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"disable\splayer_observer\s(?P<player_observer>(\S+))$", command)
        if p:
            player_observer_name = p.group("player_observer")
            chrani_bot.socketio.emit('refresh_player_observer_status', {"player_observer_name": player_observer_name}, namespace='/chrani-bot/public')
            chrani_bot.observers_controller[player_observer_name]["is_active"] = False
            response_messages.add_message("player_observer {} disabled".format(player_observer_name), True)
        else:
            response_messages.add_message("disabling player_observer failed", False)
        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "disable player_observer ",
        "usage": "/disable player_observer <name>"
    },
    "action": disable_player_observer,
    "group": "system",
    "essential": False
})


def enable_player_observer(chrani_bot, source_player, target_player, command):
    try:
        response_messages = ResponseMessage()
        p = re.search(r"enable\splayer_observer\s(?P<player_observer>(\S+))$", command)
        if p:
            player_observer_name = p.group("player_observer")
            chrani_bot.socketio.emit('refresh_player_observer_status', {"player_observer_name": player_observer_name}, namespace='/chrani-bot/public')
            chrani_bot.observers_controller[player_observer_name]["is_active"] = True
            response_messages.add_message("player_observer {} enabled".format(player_observer_name), True)
        else:
            response_messages.add_message("enabling player_observer failed", False)

        return response_messages

    except Exception as e:
        logger.debug(e)
        raise


common.actions_list.append({
    "match_mode": "startswith",
    "command": {
        "trigger": "enable player_observer ",
        "usage": "/enable player_observer <name>"
    },
    "action": enable_player_observer,
    "group": "system",
    "essential": False
})


def removeentity(chrani_bot, source_player, target_player, command):
    try:
        p = re.search(r"remove\sentity\s(?P<entity_id>[0-9]+)$", command)
        if p:
            response_messages = ResponseMessage()
            entity_id = p.group("entity_id")
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "removeentity", entity_id)
            message = "trying to remove entitiy #{} ^^".format(entity_id)
            response_messages.add_message(message, True)

            logger.info(message)
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
    "action": removeentity,
    "group": "testing",
    "essential": False
})
