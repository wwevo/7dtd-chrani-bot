from time import time
from bot.assorted_functions import get_region_string
from bot.assorted_functions import timeout_occurred
import common


def record_time_of_last_activity(self):
    current_time = time()
    if self.player_object.is_responsive() is True:
        self.player_object.last_responsive = current_time
        self.bot.players.upsert(self.player_object)
    self.player_object.last_seen = current_time
    self.player_object.update()


common.observers_dict["record_time_of_last_activity"] = {
    "type": "monitor",
    "title": "player is active",
    "action": record_time_of_last_activity,
    "env": "(self)",
    "essential": True
}


common.observers_controller["record_time_of_last_activity"] = {
    "is_active": True
}


def update_player_region(self):
    if self.player_object.is_responsive() is True:
        current_region = get_region_string(self.player_object.pos_x, self.player_object.pos_z)
        if self.player_object.region != current_region:
            self.player_object.region = get_region_string(self.player_object.pos_x, self.player_object.pos_z)
            self.player_object.update()
            self.bot.socketio.emit('refresh_player_status', {"steamid": self.player_object.steamid, "entityid": self.player_object.entityid}, namespace='/chrani-bot/public')


common.observers_dict["update_player_region"] = {
    "type": "monitor",
    "title": "player changed region",
    "action": update_player_region,
    "env": "(self)",
    "essential": True
}


common.observers_controller["update_player_region"] = {
    "is_active": True
}


def poll_playerfriends(self):
    if timeout_occurred(self.bot.players.poll_listplayerfriends_interval, self.player_object.poll_listplayerfriends_lastpoll):
        try:
            self.player_object.playerfriends_list = self.tn.listplayerfriends(self.player_object)
        except IOError:
            raise

        self.player_object.poll_listplayerfriends_lastpoll = time()
        self.player_object.update()


common.observers_dict["poll_playerfriends"] = {
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
    "env": "(self)",
    "essential": True
}


common.observers_controller["poll_playerfriends"] = {
    "is_active": True
}


def mute_unauthenticated_players(self):
    if self.bot.settings.get_setting_by_name(name="mute_unauthenticated"):
        if not self.player_object.authenticated and not self.player_object.is_muted:
            if self.tn.muteplayerchat(self.player_object, True):
                self.tn.send_message_to_player(self.player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
        elif self.player_object.authenticated and self.player_object.is_muted:
            if self.tn.muteplayerchat(self.player_object, False):
                self.tn.send_message_to_player(self.player_object, "Your chat has been enabled", color=self.bot.chat_colors['success'])
    elif self.player_object.is_muted:
        if self.tn.muteplayerchat(self.player_object, False):
            self.tn.send_message_to_player(self.player_object, "Your chat has been enabled", color=self.bot.chat_colors['success'])


common.observers_dict["mute_unauthenticated_players"] = {
    "type": "monitor",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_players,
    "env": "(self)",
    "essential": True
}


common.observers_controller["mute_unauthenticated_players"] = {
    "is_active": True
}
