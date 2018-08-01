from bot.modules.logger import logger
from time import time
from bot.assorted_functions import get_region_string
from bot.assorted_functions import timeout_occurred
import common


def record_time_of_last_activity(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        if player_object.is_responsive() is True:
            player_object.last_responsive = time()
            self.bot.players.upsert(player_object)
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
            player_object.region = get_region_string(player_object.pos_x, player_object.pos_z)
            self.bot.players.upsert(player_object)
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
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)

        if timeout_occurred(self.bot.players.poll_listplayerfriends_interval, player_object.poll_listplayerfriends_lastpoll):
            player_object.playerfriends_list = self.tn.listplayerfriends(player_object)
            player_object.poll_listplayerfriends_lastpoll = time()
            player_object.update()
            self.bot.players.upsert(player_object)

    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "poll playerfriends",
    "action": poll_playerfriends,
    "env": "(self)",
    "essential": True
})


