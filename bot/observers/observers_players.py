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
