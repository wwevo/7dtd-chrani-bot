from time import time
from bot.assorted_functions import get_region_string
from bot.assorted_functions import timeout_occurred
import common


def record_time_of_last_activity(chrani_bot, player_observer):
    current_time = time()
    if player_observer.player_object.is_responsive() is True:
        player_observer.player_object.last_responsive = current_time
        chrani_bot.players.upsert(player_observer.player_object)
    player_observer.player_object.last_seen = current_time
    player_observer.player_object.update()


common.observers_dict["record_time_of_last_activity"] = {
    "type": "monitor",
    "title": "player is active",
    "action": record_time_of_last_activity,
    "essential": True
}


common.observers_controller["record_time_of_last_activity"] = {
    "is_active": True
}


def update_player_region(chrani_bot, player_observer):
    if player_observer.player_object.is_responsive() is True:
        current_region = get_region_string(player_observer.player_object.pos_x, player_observer.player_object.pos_z)
        if player_observer.player_object.region != current_region:
            player_observer.player_object.region = get_region_string(player_observer.player_object.pos_x, player_observer.player_object.pos_z)
            player_observer.player_object.update()
            chrani_bot.socketio.emit('refresh_player_status', {"steamid": player_observer.player_object.steamid, "entityid": player_observer.player_object.entityid}, namespace='/chrani-bot/public')


common.observers_dict["update_player_region"] = {
    "type": "monitor",
    "title": "player changed region",
    "action": update_player_region,
    "essential": True
}


common.observers_controller["update_player_region"] = {
    "is_active": True
}


def poll_playerfriends(chrani_bot, player_thread):
    if timeout_occurred(chrani_bot.players.poll_listplayerfriends_interval, player_thread.player_object.poll_listplayerfriends_lastpoll):
        try:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "lpf", player_thread.player_object)
        except IOError:
            return False

        player_thread.player_object.poll_listplayerfriends_lastpoll = time()
        player_thread.player_object.update()


common.observers_dict["poll_playerfriends"] = {
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
    "essential": True
}


common.observers_controller["poll_playerfriends"] = {
    "is_active": True
}


def mute_unauthenticated_players(chrani_bot, player_observer):
    if chrani_bot.settings.get_setting_by_name(name="mute_unauthenticated"):
        if player_observer.player_object.has_been_muted is None:
            if not player_observer.player_object.authenticated and not player_observer.player_object.is_muted:
                player_observer.player_object.has_been_muted = True
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_observer.player_object, True)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, "Your chat has been disabled!", chrani_bot.chat_colors['warning'])
            elif player_observer.player_object.authenticated and player_observer.player_object.is_muted:
                player_observer.player_object.has_been_muted = False
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_observer.player_object, False)
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, "Your chat has been enabled!", chrani_bot.chat_colors['warning'])
    elif player_observer.player_object.is_muted and player_observer.player_object.has_been_muted is None:
        player_observer.player_object.has_been_muted = False
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_observer.player_object, False)
        chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_observer.player_object, "Your chat has been enabled", chrani_bot.chat_colors['success'])


common.observers_dict["mute_unauthenticated_players"] = {
    "type": "monitor",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_players,
    "essential": True
}


common.observers_controller["mute_unauthenticated_players"] = {
    "is_active": True
}
