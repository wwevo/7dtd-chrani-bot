import re
from assorted_functions import timeout_occurred
import time
from bot.logger import logger

observers_scheduler = []


def mute_unauthenticated_player(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        if self.bot.settings_dict["mute_unauthenticated"] is True:
            if player_object.authenticated is not True:
                if self.tn.muteplayerchat(player_object, True):
                    self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
            else:
                if self.tn.muteplayerchat(player_object, False):
                    self.tn.send_message_to_player(player_object, "Your chat has been enabled", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


observers_scheduler.append(("monitor", "mute unauthenticated players", mute_unauthenticated_player, "(self)"))
