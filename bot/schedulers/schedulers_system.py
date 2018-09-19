import time
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred
import common


def poll_players(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                listplayers_interval = float(bot.settings.get_setting_by_name('list_players_interval_idle'))
            except TypeError:
                return True
        else:
            listplayers_interval = float(bot.settings.get_setting_by_name('list_players_interval'))

        if timeout_occurred(listplayers_interval, float(common.schedulers_dict["poll_players"]["last_executed"])):
            bot.players.manage_online_players(bot)
            common.schedulers_dict["poll_players"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug(e)
        raise


common.schedulers_dict["poll_players"] = {
    "type": "schedule",
    "title": "poll players",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": poll_players,
    "env": "(self)",
    "essential": True
}


def update_system_status(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                update_status_interval = float(bot.settings.get_setting_by_name('list_status_interval_idle'))
            except TypeError:
                return True
        else:
            update_status_interval = float(bot.settings.get_setting_by_name('list_status_interval'))

        if timeout_occurred(update_status_interval, float(common.schedulers_dict["update_system_status"]["last_executed"])):
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
        logger.debug(e)
        raise


common.schedulers_dict["update_system_status"] = {
    "type": "schedule",
    "title": "update system status",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": update_system_status,
    "env": "(self)",
    "essential": True
}


def list_landprotection(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                listlandprotection_interval = float(bot.settings.get_setting_by_name('list_landprotection_interval_idle'))
            except TypeError:
                return True
        else:
            listlandprotection_interval = float(bot.settings.get_setting_by_name('list_landprotection_interval'))

        if timeout_occurred(listlandprotection_interval, float(common.schedulers_dict["list_landprotection"]["last_executed"])):
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
        logger.debug(e)
        raise


common.schedulers_dict["list_landprotection"] = {
    "type": "schedule",
    "title": "list land protection",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": "0",
    "action": list_landprotection,
    "env": "(self)",
    "essential": True
}




