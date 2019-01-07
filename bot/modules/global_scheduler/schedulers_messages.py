import time
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred
import common
import random


def rolling_announcements(chrani_bot):
    try:
        if len(chrani_bot.dom.get("bot_data").get("active_threads").get("player_observer")) == 0:  # adjust poll frequency when the server is empty
            return True

        if timeout_occurred(float(chrani_bot.settings.get_setting_by_name(name='rolling_announcements_interval')), float(common.schedulers_dict["rolling_announcements"]["last_executed"])):
            message, interval = random.choice(list(chrani_bot.settings.get_setting_by_name(name='rolling_announcements').items()))
            if interval == "all":
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['standard'])
            if interval == "day7" and chrani_bot.is_it_horde_day(int(chrani_bot.dom["game_data"]["gametime"]["day"])):
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", message, chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['standard'])
            common.schedulers_dict["rolling_announcements"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug("{source}/{error_message}".format(source="rolling_announcements", error_message=e.message))
        raise


common.schedulers_dict["rolling_announcements"] = {
    "type": "schedule",
    "title": "rolling announcements",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": time.time(),
    "action": rolling_announcements,
    }


common.schedulers_controller["rolling_announcements"] = {
    "is_active": True,
    "essential": False
}
