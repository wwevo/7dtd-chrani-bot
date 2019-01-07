import os
import time
import __main__

actions_dict = {}
active_actions_dict = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module == 'common.py' or module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module


def set_active_action_status(steamid, command, status=True):
    try:
        active_actions_dict[steamid][command].update({
            "status": status,
            "last_executed": time.time(),
        })
        return True
    except KeyError:
        pass

    try:
        active_actions_dict[steamid][command] = {
            "status": status,
            "last_executed": time.time(),
        }
        return True
    except KeyError:
        pass

    try:
        active_actions_dict[steamid] = {}
        active_actions_dict[steamid][command] = {
            "status": status,
            "last_executed": time.time(),
        }
    except KeyError:
        pass


def set_active_action_result(steamid, command, result):
    try:
        active_actions_dict[steamid][command]["result"] = result
    except KeyError:
        return None


def get_active_action_status(steamid, command):
    try:
        return active_actions_dict[steamid][command]["status"]
    except KeyError:
        return False


def get_active_action_result(steamid, command):
    try:
        return active_actions_dict[steamid][command]["result"]
    except KeyError:
        return ""


def get_active_action_last_executed(steamid, command):
    try:
        return active_actions_dict[steamid][command]["last_executed"]
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
