from bot.modules.logger import logger
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


common.observers_list.append({
    "type": "monitor",
    "title": "player is active",
    "action": record_time_of_last_activity,
    "env": "(self)",
    "essential": True
})


def update_player_region(self):
    if self.player_object.is_responsive() is True:
        current_region = get_region_string(self.player_object.pos_x, self.player_object.pos_z)
        if self.player_object.region != current_region:
            self.player_object.region = get_region_string(self.player_object.pos_x, self.player_object.pos_z)
            self.player_object.update()
            self.bot.socketio.emit('refresh_player_status', {"steamid": self.player_object.steamid, "entityid": self.player_object.entityid}, namespace='/chrani-bot/public')


common.observers_list.append({
    "type": "monitor",
    "title": "player changed region",
    "action": update_player_region,
    "env": "(self)",
    "essential": True
})


def poll_playerfriends(self):
    if timeout_occurred(self.bot.players.poll_listplayerfriends_interval, self.player_object.poll_listplayerfriends_lastpoll):
        self.player_object.playerfriends_list = self.tn.listplayerfriends(self.player_object)
        self.player_object.poll_listplayerfriends_lastpoll = time()
        self.player_object.update()


common.observers_list.append({
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
    "env": "(self)",
    "essential": True
})


def mute_unauthenticated_player(self, player_object=None):
    if player_object.authenticated is not True:
        if self.tn.muteplayerchat(player_object, True):
            self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.chat_colors['warning'])
    else:
        if self.tn.muteplayerchat(player_object, False):
            self.tn.send_message_to_player(player_object, "Your chat has been enabled", color=self.chat_colors['success'])


common.observers_list.append({
    "type": "trigger",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_player,
    "env": "(self, player_object)",
    "essential": True
})


