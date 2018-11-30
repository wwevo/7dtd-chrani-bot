import re
import time
import threading
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred
from bot.assorted_functions import timepassed_occurred
import common


def get_mem_status(bot):
    try:
        if not bot.reboot_imminent and timeout_occurred(0.25 * 60, float(
                common.schedulers_dict["get_mem_status"]["last_executed"])):
            mem_status = bot.telnet_observer.tn.get_mem_status()
            common.schedulers_dict["get_mem_status"]["last_executed"] = time.time()
            # m = re.search(bot.match_types_system["mem_status"], mem_status)
            # if m:
            #     bot.server_time_running = int(float(m.group("time_in_minutes")) * 60)

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
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["get_mem_status"] = {
    "is_active": True
}


def poll_players(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                listplayers_interval = float(bot.settings.get_setting_by_name(name='list_players_interval_idle'))
            except TypeError:
                return True
        else:
            listplayers_interval = float(bot.settings.get_setting_by_name(name='list_players_interval'))

        if timeout_occurred(listplayers_interval, float(common.schedulers_dict["poll_players"]["last_executed"])):
            bot.players.manage_online_players(bot)
            common.schedulers_dict["poll_players"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="poll_players", error_message=e.message))
        raise


common.schedulers_dict["poll_players"] = {
    "type": "schedule",
    "title": "poll players",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": poll_players,
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["poll_players"] = {
    "is_active": True
}


def get_gametime(bot):
    try:
        if timeout_occurred(2.5, float(common.schedulers_dict["get_gametime"]["last_executed"])):
            game_time = bot.poll_tn.gettime()
            common.schedulers_dict["get_gametime"]["last_executed"] = time.time()
            p = re.search(r"^Day\s(?P<day>\d{1,5}),\s(?P<hour>\d{1,2}):(?P<minute>\d{1,2}).*\r\n", game_time)
            if p:
                bot.current_gametime = {
                    "day": p.group("day"),
                    "hour": p.group("hour"),
                    "minute": p.group("minute")
                }
            else:
                bot.current_gametime = None
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
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["get_gametime"] = {
    "is_active": True
}


def update_system_status(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                update_status_interval = float(bot.settings.get_setting_by_name(name='list_status_interval_idle'))
            except TypeError:
                return True
        else:
            update_status_interval = float(bot.settings.get_setting_by_name(name='list_status_interval'))

        if timeout_occurred(update_status_interval, float(
                common.schedulers_dict["update_system_status"]["last_executed"])):
            bot.socketio.emit('server_online', '', namespace='/chrani-bot/public')
            bot.socketio.emit('refresh_status', '', namespace='/chrani-bot/public')
            execution_time = 0.0
            count = 0
            for player_steamid, player_dict in bot.active_player_threads_dict.iteritems():
                count = count + 1
                execution_time += player_dict["thread"].last_execution_time
            if count > 0:
                bot.oberservers_execution_time = execution_time / count
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
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["update_system_status"] = {
    "is_active": True
}


def list_landprotection(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                listlandprotection_interval = float(bot.settings.get_setting_by_name(name='list_landprotection_interval_idle'))
            except TypeError:
                return True
        else:
            listlandprotection_interval = float(bot.settings.get_setting_by_name(name='list_landprotection_interval'))

        if timeout_occurred(listlandprotection_interval, float(
                common.schedulers_dict["list_landprotection"]["last_executed"])):
            if len(bot.active_player_threads_dict) > 0 or not bot.landclaims_dict:
                polled_lcb = bot.poll_lcb()
                if polled_lcb != bot.landclaims_dict:
                    lcb_owners_to_delete = {}
                    lcb_owners_to_update = {}
                    lcb_owners_to_update.update(polled_lcb)
                    for lcb_widget_owner in lcb_owners_to_update.keys():
                        try:
                            player_object = bot.players.get_by_steamid(lcb_widget_owner)
                        except KeyError:
                            continue

                        bot.socketio.emit('refresh_player_lcb_widget', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')

                    bot.socketio.emit('update_leaflet_markers', bot.get_lcb_marker_json(lcb_owners_to_update), namespace='/chrani-bot/public')
                    bot.socketio.emit('remove_leaflet_markers', bot.get_lcb_marker_json(lcb_owners_to_delete), namespace='/chrani-bot/public')
                    bot.landclaims_dict = polled_lcb

            common.schedulers_dict["list_landprotection"]["last_executed"] = time.time()
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
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["list_landprotection"] = {
    "is_active": True
}


def reboot(bot):
    """ this function is special as it will start a timer-threrad to initiate the shutdown procedures """
    def reboot_worker():
        restart_timer = bot.settings.get_setting_by_name(name='restart_warning')
        message = "server will restart in {} seconds".format(restart_timer)
        bot.tn.say(message, color=bot.chat_colors['warning'])
        bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot" , message)}, namespace='/chrani-bot/public')
        common.schedulers_dict["reboot"]["current_countdown"] = 0
        while True:
            time.sleep(1)
            common.schedulers_dict["reboot"]["current_countdown"] += 1
            if common.schedulers_dict["reboot"]["current_countdown"] == int(restart_timer / 2):
                message = "server will restart in {} seconds".format(int(restart_timer / 2))
                bot.tn.say(message, color=bot.chat_colors['warning'])
                bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot" , message)}, namespace='/chrani-bot/public')
            if common.schedulers_dict["reboot"]["current_countdown"] == restart_timer - 60:
                message = "server will restart in {} seconds".format(60)
                bot.tn.say(message, color=bot.chat_colors['warning'])
                bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot" , message)}, namespace='/chrani-bot/public')
            if common.schedulers_dict["reboot"]["current_countdown"] == restart_timer - 15:
                message = "server will restart NOW!"
                bot.tn.say(message, color=bot.chat_colors['warning'])
                bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot" , message)}, namespace='/chrani-bot/public')
                common.schedulers_dict["reboot"]["current_countdown"] = 0
                bot.tn.shutdown()
                return True

    try:
        if bot.server_time_running is not None:
            bot.restart_in = bot.settings.get_setting_by_name(name='restart_timer') - bot.server_time_running

        if bot.ongoing_bloodmoon() or bot.reboot_imminent:
            return True

        if bot.server_time_running is not None and timepassed_occurred(bot.settings.get_setting_by_name(name='restart_timer') - bot.settings.get_setting_by_name(name='restart_warning'), bot.server_time_running):
            bot.reboot_imminent = True
            bot.server_time_running = None
            bot.reboot_thread = threading.Thread(target=reboot_worker)
            bot.reboot_thread.start()

            message = "server restart procedures initiated..."
            bot.tn.say(message, color=bot.chat_colors['warning'])
            bot.socketio.emit('status_log', {"steamid": "system", "name": "system", "command": "{}:{} = {}".format("scheduler", "reboot" , message)}, namespace='/chrani-bot/public')

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
    "env": "(self)",
    "essential": True,
}


common.schedulers_controller["reboot"] = {
    "is_active": True
}