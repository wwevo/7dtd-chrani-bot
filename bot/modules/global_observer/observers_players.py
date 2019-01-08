from time import time
from bot.assorted_functions import get_region_string
from bot.assorted_functions import timeout_occurred
import common


def record_time_of_last_activity(chrani_bot, player_thread):
    current_time = time()
    if player_thread.player_object.is_responsive() is True:
        chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["last_responsive"] = current_time

    chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["last_seen"] = current_time
    player_thread.player_object.last_seen = current_time
    # chrani_bot.players.upsert(player_thread.player_object, save=True)


common.observers_dict["record_time_of_last_activity"] = {
    "type": "monitor",
    "title": "player is active",
    "action": record_time_of_last_activity
}


common.observers_controller["record_time_of_last_activity"] = {
    "is_active": True,
    "is_essential": False
}


def update_player_region(chrani_bot, player_thread):
    if player_thread.player_object.is_responsive() is True:
        current_region = get_region_string(chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["pos_x"], chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["pos_z"])
        if chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["region"] != current_region:
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["region"] = current_region
            player_thread.player_object.region = current_region
            chrani_bot.players.upsert(player_thread.player_object, save=True)


common.observers_dict["update_player_region"] = {
    "type": "monitor",
    "title": "player changed region",
    "action": update_player_region,
}


common.observers_controller["update_player_region"] = {
    "is_active": True,
    "is_essential": False
}


def poll_playerfriends(chrani_bot, player_thread):
    if timeout_occurred(chrani_bot.settings.get_setting_by_name(name="list_playerfriends_interval"), chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("poll_listplayerfriends_lastpoll", 0)):
        try:
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="listplayerfriends_method", default="lpf"), player_thread.player_object)
        except IOError:
            return False

        chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["poll_listplayerfriends_lastpoll"] = time()


common.observers_dict["poll_playerfriends"] = {
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
}


common.observers_controller["poll_playerfriends"] = {
    "is_active": True,
    "is_essential": False
}


def mute_unauthenticated_players(chrani_bot, player_thread):
    """ beware: is_allowed_to_chat is a STRING!"""
    player_object = player_thread.player_object
    if chrani_bot.settings.get_setting_by_name(name="mute_unauthenticated"):
        # we only mute when it's enabled in the settings
        if chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("authenticated", False):
            # nothing to mute
            return
        if chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("is_allowed_to_chat", "None") == "None":
            # player has been manually muted and the chat status has not been set yet
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, True)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "False"
            return
        if chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] == "True":
            # player has been manually muted and the chat status is set to enabled
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, True)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "False"
            return
        if not chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("authenticated", False) and chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("is_allowed_to_chat", "None") == "None":
            # player is not authenticated and the chat status has not been set yet
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, True)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "False"
            return
        if not chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("authenticated", False) and chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] == "True":
            # player is not authenticated and the chat status has been set to enabled
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, True)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "False"
            return


common.observers_dict["mute_unauthenticated_players"] = {
    "type": "monitor",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_players,
}


common.observers_controller["mute_unauthenticated_players"] = {
    "is_active": True,
    "is_essential": True
}


def unmute_authenticated_players(chrani_bot, player_thread):
    """ beware: is_allowed_to_chat is a STRING!"""
    player_object = player_thread.player_object
    if not chrani_bot.settings.get_setting_by_name(name="mute_unauthenticated"):
        # we don't mute unauthenticated players. so we unmute every player that's not manually muted
        if not chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("is_allowed_to_chat", "None") == "None":
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, False)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "True"
            return
        if not chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] == "False":
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, False)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "True"
            return
    else:
        if chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("authenticated", False) and not chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("is_allowed_to_chat", "None") == "None":
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, False)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "True"
            return
        if chrani_bot.dom.get("bot_data").get("player_data").get(player_thread.player_steamid).get("authenticated", False) and not chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_muted"] and chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] == "False":
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, chrani_bot.settings.get_setting_by_name(name="mute_method"), player_object, False)
            chrani_bot.dom["bot_data"]["player_data"][player_thread.player_steamid]["is_allowed_to_chat"] = "True"
            return


common.observers_dict["unmute_authenticated_players"] = {
    "type": "monitor",
    "title": "unmute authenticated players",
    "action": unmute_authenticated_players,
}


common.observers_controller["unmute_authenticated_players"] = {
    "is_active": True,
    "is_essential": True
}
