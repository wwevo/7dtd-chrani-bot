import time
import math
import re

from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


class TelnetActions:
    tn = object
    bot = object
    last_line = str

    exclusive_actions = dict
    timeout = int

    def __init__(self, bot, telnet_connection):
        self.bot = bot
        self.timeout = self.bot.settings.get_setting_by_name(name='list_players_interval')
        self.last_line = ""
        self.tn = telnet_connection.tn
        self.exclusive_actions = {
            "listplayers": False,
        }

    def settime(self, time_string):
        command = "settime {}\r\n".format(str(time_string))
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

    def debuffplayer(self, player_object, buff):
        if not player_object.is_online:
            return False

        buff_list = [
            "bleeding",
            "foodPoisoning",
            "brokenLeg",
            "sprainedLeg"
        ]
        if buff not in buff_list:
            return False
        try:
            connection = self.tn
            command = "debuffplayer {player_steamid} {buff} {lbr}".format(player_steamid=player_object.steamid, buff=buff, lbr=b"\r\n")
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def buffplayer(self, player_object, buff):
        if not player_object.is_online:
            return False

        buff_list = [
            "firstAidLarge"
        ]
        if buff not in buff_list:
            return False
        try:
            connection = self.tn
            command = "buffplayer " + str(player_object.steamid) + " " + str(buff) + "\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def set_admin_level(self, player_object, level):
        allowed_levels = [
            "2", "4"
        ]
        if level not in allowed_levels:
            return False
        try:
            connection = self.tn
            command = "admin add " + player_object.steamid + " " + str(level) + "\r\n"
            logger.info(command)
            connection.write(command)
        except Exception:
            return False

    def shutdown(self):
        connection = self.tn
        command = "shutdown\r\n"
        logger.info(command)
        try:
            connection.write(command)
        except Exception:
            return False

    def saveworld(self):
        connection = self.tn
        command = "saveworld\r\n"
        logger.info(command)
        try:
            connection.write(command)
        except Exception:
            return False

    def remove_entity(self, entity_id):
        command = "removeentity " + str(entity_id) + b"\r\n"
        try:
            connection = self.tn
            connection.write(command)
            return True
        except Exception:
            return False

