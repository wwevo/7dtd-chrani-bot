from bot.modules.logger import logger
from time import time
from bot.assorted_functions import get_region_string
from bot.assorted_functions import timeout_occurred
import common


def record_time_of_last_activity(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        current_time = time()
        if player_object.is_responsive() is True:
            player_object.last_responsive = current_time
            self.bot.players.upsert(player_object)
        player_object.last_seen = current_time
        player_object.update()
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "player is active",
    "action": record_time_of_last_activity,
    "env": "(self)",
    "essential": True
})


def update_player_region(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        if player_object.is_responsive() is True:
            current_region = get_region_string(player_object.pos_x, player_object.pos_z)
            if player_object.region != current_region:
                player_object.region = get_region_string(player_object.pos_x, player_object.pos_z)
                player_object.update()
                self.bot.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "player changed region",
    "action": update_player_region,
    "env": "(self)",
    "essential": True
})


def poll_playerfriends(self):
    player_object = self.bot.players.get_by_steamid(self.player_steamid)

    if timeout_occurred(self.bot.players.poll_listplayerfriends_interval, player_object.poll_listplayerfriends_lastpoll):
        player_object.playerfriends_list = self.tn.listplayerfriends(player_object)
        player_object.poll_listplayerfriends_lastpoll = time()
        player_object.update()
        self.bot.socketio.emit('update_player_table_row', {"steamid": player_object.steamid, "entityid": player_object.entityid}, namespace='/chrani-bot/public')


common.observers_list.append({
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
    "env": "(self)",
    "essential": True
})


def initialize_player(self):
    if self.player_object.initialized is not True:
        player_moved_mouse = False
        if self.player_object.old_rot_x != self.player_object.rot_x:
            player_moved_mouse = True
        # if player_object.old_rot_y != player_object.rot_y:
        #     player_moved_mouse = True
        if self.player_object.old_rot_z != self.player_object.rot_z:
            player_moved_mouse = True

        if player_moved_mouse is True:
            self.player_object.initialized = True
            logger.debug("{} has been caught moving their head :)".format(self.player_object.name))
            return True

    return False


common.observers_list.append({
    "type": "monitor",
    "title": "initialize player",
    "action": initialize_player,
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


