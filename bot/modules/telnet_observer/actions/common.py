import os
import time
import __main__

actions_dict = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module == 'common.py' or module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module


def set_active_action_status(steamid, command, status=True):
    chrani_bot = __main__.chrani_bot
    try:
        chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command].update({
            "status": status,
            "last_executed": time.time(),
        })
        return True
    except KeyError:
        pass

    try:
        chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command] = {
            "status": status,
            "last_executed": time.time(),
        }
        return True
    except KeyError:
        pass

    try:
        chrani_bot.dom["bot_data"]["telnet_observer"][steamid] = {}
        chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command] = {
            "status": status,
            "last_executed": time.time(),
        }
    except KeyError:
        pass


def set_active_action_result(steamid, command, result):
    chrani_bot = __main__.chrani_bot
    try:
        chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command]["result"] = result
    except KeyError:
        return None


def get_active_action_status(steamid, command):
    chrani_bot = __main__.chrani_bot
    try:
        return chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command]["status"]
    except KeyError:
        return False


def get_active_action_result(steamid, command):
    chrani_bot = __main__.chrani_bot
    try:
        return chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command]["result"]
    except KeyError:
        return ""


def get_active_action_last_executed(steamid, command):
    chrani_bot = __main__.chrani_bot
    try:
        return chrani_bot.dom["bot_data"]["telnet_observer"][steamid][command]["last_executed"]
    except KeyError:
        return False


def trigger_action(bot, action, *args, **kwargs):
    try:
        if len(args) == 0:
            return actions_dict[action]["action"]()
        elif len(args) >= 1:
            return actions_dict[action]["action"](*args, **kwargs)
    except IOError:
        raise
    except KeyError:
        pass
    except TypeError:
        pass
