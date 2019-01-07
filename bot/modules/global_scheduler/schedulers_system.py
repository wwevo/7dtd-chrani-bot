import re
import time
import threading
import traceback
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred
from bot.assorted_functions import timepassed_occurred
import common


def set_chat_prefix(chrani_bot):
    try:
        if timeout_occurred(2, float(common.schedulers_dict["set_chat_prefix"]["last_executed"])):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name='chatprefix_method'))
            common.schedulers_dict["set_chat_prefix"]["last_executed"] = time.time()
            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="set_chat_prefix", error_message=e.message))
        raise


common.schedulers_dict["set_chat_prefix"] = {
    "type": "schedule",
    "title": "set chat prefix",
    "trigger": "interval",
    "last_executed": "0",
    "action": set_chat_prefix,
    "env": "(self)"
}


common.schedulers_controller["set_chat_prefix"] = {
    "is_active": True,
    "essential": True
}


def get_game_preferences(chrani_bot):
    try:
        if timeout_occurred(5, float(common.schedulers_dict["get_game_preferences"]["last_executed"])):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "gg")
            common.schedulers_dict["get_game_preferences"]["last_executed"] = time.time()
            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="get_game_preferences", error_message=e.message))
        raise


common.schedulers_dict["get_game_preferences"] = {
    "type": "schedule",
    "title": "get game preferences",
    "trigger": "interval",
    "last_executed": "0",
    "action": get_game_preferences,
    }


common.schedulers_controller["get_game_preferences"] = {
    "is_active": True,
    "essential": True
}


def get_mem_status(chrani_bot):
    try:
        if timeout_occurred(0.25 * 60, float(common.schedulers_dict["get_mem_status"]["last_executed"])):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "mem")
            common.schedulers_dict["get_mem_status"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="get_mem_status", error_message=e.message))
        raise


common.schedulers_dict["get_mem_status"] = {
    "type": "schedule",
    "title": "get mem status",
    "trigger": "interval",
    "last_executed": "0",
    "action": get_mem_status,
    }


common.schedulers_controller["get_mem_status"] = {
    "is_active": True,
    "essential": False
}


def poll_players(chrani_bot):
    try:
        if len(chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer")) == 0 and not chrani_bot.first_run and chrani_bot.dom["bot_data"]["time_running"] >= 30:  # adjust poll frequency when the server is empty
            try:
                listplayers_interval = float(chrani_bot.settings.get_setting_by_name(name='list_players_interval_idle'))
            except TypeError:
                return True
        else:
            listplayers_interval = float(chrani_bot.settings.get_setting_by_name(name='list_players_interval'))

        if timeout_occurred(listplayers_interval, float(common.schedulers_dict["poll_players"]["last_executed"])):
            # logger.debug("{source}/{error_message}".format(source="poll_players", error_message="about to execute!"))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name='listplayers_method'))
            common.schedulers_dict["poll_players"]["last_executed"] = time.time()

            return True
    except Exception as e:
        traceback.print_exc()
        logger.debug("{source}/{error_message}".format(source="poll_players", error_message=e.message))
        raise


common.schedulers_dict["poll_players"] = {
    "type": "schedule",
    "title": "poll players",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": poll_players,
    }


common.schedulers_controller["poll_players"] = {
    "is_active": True,
    "essential": True
}


def get_gametime(chrani_bot):
    try:
        if timeout_occurred(10, float(common.schedulers_dict["get_gametime"]["last_executed"])):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "gt")
            common.schedulers_dict["get_gametime"]["last_executed"] = time.time()

            p = re.search(r"Day\s(?P<day>\d{1,5}),\s(?P<hour>\d{1,2}):(?P<minute>\d{1,2})", chrani_bot.telnet_observer.actions.common.get_active_action_result("system", "gt"))
            if p:
                chrani_bot.dom["game_data"]["gametime"] = {
                    "day": p.group("day"),
                    "hour": p.group("hour"),
                    "minute": p.group("minute")
                }
            else:
                chrani_bot.dom["game_data"]["gametime"] = None
            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="get_gametime", error_message=e.message))
        raise


common.schedulers_dict["get_gametime"] = {
    "type": "schedule",
    "title": "get gametime",
    "trigger": "interval",
    "last_executed": "0",
    "action": get_gametime,
    }


common.schedulers_controller["get_gametime"] = {
    "is_active": True,
    "essential": False
}


def update_system_status(bot):
    try:
        if len(bot.dom.get("bot_data").get("active_threads").get("player_observer")) == 0:  # adjust poll frequency when the server is empty
            try:
                update_status_interval = float(bot.settings.get_setting_by_name(name='list_status_interval_idle'))
            except TypeError:
                return True
        else:
            update_status_interval = float(bot.settings.get_setting_by_name(name='list_status_interval'))

        if timeout_occurred(update_status_interval, float(
                common.schedulers_dict["update_system_status"]["last_executed"])):
            # bot.socketio.emit('server_online', '', namespace='/chrani-bot/public')
            bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
            execution_time = 0.0
            count = 0
            for player_steamid, player_thread in bot.dom.get("bot_data").get("active_threads").get("player_observer").iteritems():
                count = count + 1
                execution_time += player_thread.last_execution_time
            common.schedulers_dict["update_system_status"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="update_system_status", error_message=e.message))
        raise


common.schedulers_dict["update_system_status"] = {
    "type": "schedule",
    "title": "update system status",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": update_system_status,
    "env": "(self)"
}


common.schedulers_controller["update_system_status"] = {
    "is_active": True,
    "essential": False
}


def list_landprotection(chrani_bot):
    try:
        if len(chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer")) == 0:  # adjust poll frequency when the server is empty
            try:
                listlandprotection_interval = float(chrani_bot.settings.get_setting_by_name(name='list_landprotection_interval_idle'))
            except TypeError:
                return True
        else:
            listlandprotection_interval = float(chrani_bot.settings.get_setting_by_name(name='list_landprotection_interval'))

        if timeout_occurred(listlandprotection_interval, float(common.schedulers_dict["list_landprotection"]["last_executed"])):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "llp")
            common.schedulers_dict["list_landprotection"]["last_executed"] = time.time()
            chrani_bot.manage_landclaims()
            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="list_landprotection", error_message=e.message))
        raise


common.schedulers_dict["list_landprotection"] = {
    "type": "schedule",
    "title": "list land protection",
    "trigger": "interval",  # "interval, timepassed, gametime, gameday"
    "last_executed": "0",
    "action": list_landprotection,
    }


common.schedulers_controller["list_landprotection"] = {
    "is_active": True,
    "essential": False
}


def reboot(chrani_bot):
    """ this function is special as it will start a timer-threrad to initiate the shutdown procedures """
    def reboot_worker():
        restart_timer = chrani_bot.settings.get_setting_by_name(name='restart_warning')
        message = "server will restart in {} seconds".format(restart_timer)
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['warning'])
        chrani_bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot", message)}, namespace='/chrani-bot/public')
        common.schedulers_dict["reboot"]["current_countdown"] = 0
        while True:
            time.sleep(1)
            common.schedulers_dict["reboot"]["current_countdown"] += 1
            if common.schedulers_dict["reboot"]["current_countdown"] == int(restart_timer / 2):
                message = "server will restart in {} seconds".format(int(restart_timer / 2))
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say",message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['warning'])
                chrani_bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot", message)}, namespace='/chrani-bot/public')
            if common.schedulers_dict["reboot"]["current_countdown"] == restart_timer - 60:
                message = "server will restart in {} seconds".format(60)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say",message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['warning'])
                chrani_bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot", message)}, namespace='/chrani-bot/public')
            if common.schedulers_dict["reboot"]["current_countdown"] >= restart_timer - 15:
                message = "server will restart NOW!"
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say",message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['warning'])
                chrani_bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot", message)}, namespace='/chrani-bot/public')
                common.schedulers_dict["reboot"]["current_countdown"] = 0
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "shutdown")
                return True

    try:
        if chrani_bot.dom.get("game_data").get("time_running", False):
            chrani_bot.dom["game_data"]["restart_in"] = chrani_bot.settings.get_setting_by_name(name='restart_timer') - chrani_bot.dom["game_data"]["time_running"]

        if chrani_bot.ongoing_bloodmoon() or chrani_bot.dom.get("bot_data").get("active_threads").get("schedulers_system").get("reboot", False):
            return True

        if chrani_bot.dom["game_data"]["time_running"] is not None and timepassed_occurred(chrani_bot.settings.get_setting_by_name(name='restart_timer') - chrani_bot.settings.get_setting_by_name(name='restart_warning'), chrani_bot.dom["game_data"]["time_running"]):
            chrani_bot.reboot_imminent = True
            reboot_thread = threading.Thread(target=reboot_worker, name="reboot")
            chrani_bot.dom["bot_data"]["active_threads"]["schedulers_system"]["reboot"] = reboot_thread
            reboot_thread.start()

            message = "server restart procedures initiated..."
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say",message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['warning'])
            chrani_bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot", message)}, namespace='/chrani-bot/public')

            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="reboot", error_message=e.message))
        raise


common.schedulers_dict["reboot"] = {
    "type": "schedule",
    "title": "reboot",
    "trigger": "timepassed",  # "interval, gametime, gameday"
    "last_executed": time.time(),
    "action": reboot,
    }


common.schedulers_controller["reboot"] = {
    "is_active": True,
    "essential": True
}
