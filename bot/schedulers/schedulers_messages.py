import time
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred
import common
import random


def rolling_announcements(bot):
    try:
        if len(bot.active_player_threads_dict) == 0:  # adjust poll frequency when the server is empty
            try:
                rolling_announcements_interval = float(bot.settings.get_setting_by_name('rolling_announcements_interval_idle'))
            except TypeError:
                return True
        else:
            rolling_announcements_interval = float(bot.settings.get_setting_by_name('rolling_announcements_interval'))

        if timeout_occurred(rolling_announcements_interval, float(common.schedulers_dict["rolling_announcements"]["last_executed"])):
            message = random.choice(bot.settings.get_setting_by_name('rolling_announcements'))
            bot.tn.say(message, color=bot.chat_colors['background'])
            common.schedulers_dict["rolling_announcements"]["last_executed"] = time.time()

            return True
    except Exception as e:
        logger.debug(e)
        raise


common.schedulers_dict["rolling_announcements"] = {
    "type": "schedule",
    "title": "rolling announcements",
    "trigger": "interval",  # "interval, gametime, gameday"
    "last_executed": time.time(),
    "action": rolling_announcements,
    "env": "(self)",
    "essential": True
}
