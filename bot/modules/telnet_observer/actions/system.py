import __main__
import common
import re
import time
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def mem():
    chrani_bot = __main__.chrani_bot
    command = "mem"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def mem_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "mem"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Time:\s(?P<time_in_minutes>.*)m\sFPS:\s(?P<server_fps>.*)\sHeap:\s(?P<heap>.*)MB\sMax:\s(?P<max>.*)MB\sChunks:\s(?P<chunks>.*)\sCGO:\s(?P<cgo>.*)\sPly:\s(?P<players>.*)\sZom:\s(?P<zombies>.*)\sEnt:\s(?P<entities>.*\s\(.*\))\sItems:\s(?P<items>.*)\sCO:\s(?P<co>.*)\sRSS:\s(?P<rss>.*)MB", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result('system', command, match.group(0))
            chrani_bot.server_time_running = int(float(match.group("time_in_minutes")) * 60)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["mem"] = {
    "telnet_command": "mem",
    "action": mem,
    "action_callback": mem_callback_thread,
    "is_available": True
}


def gt():
    chrani_bot = __main__.chrani_bot
    command = "gt"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting 'gt'")
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command 'gt' is active and waiting for a response!")


def gt_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "gt"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Day\s(\d{1,5}),\s(\d{1,2}):(\d{1,2}).*", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["gt"] = {
    "telnet_command": "gt",
    "action": gt,
    "action_callback": gt_callback_thread,
    "is_available": True
}


def gg():
    chrani_bot = __main__.chrani_bot
    command = "gg"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting 'gg'")
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command 'gg' is active and waiting for a response!")


def gg_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "gg"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(10, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'gg\' by Telnet from (.*)([\s\S]+?)GamePref.ZombiesRun = (\d{1,2})\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            game_preferences_raw = match.group(0)
            game_preferences_dict = {}
            if game_preferences_raw != "":
                game_preferences = game_preferences_raw.strip()
                game_preferences_list = re.findall(r"GamePref\.(?P<key>.*)\s=\s(?P<value>.*)\r\n", game_preferences)

                if game_preferences:
                    logger.debug(game_preferences_list)
                    for key, value in game_preferences_list:
                        game_preferences_dict.update({
                            key: value
                        })
            common.set_active_action_result('system', command, game_preferences_dict)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["gg"] = {
    "telnet_command": "gg",
    "action": gg,
    "action_callback": gg_callback_thread,
    "is_available": True
}


def tcch():
    chrani_bot = __main__.chrani_bot
    command = "tcch"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write('{command} \"/\" {line_end}'.format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def tcch_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "tcch"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " \"(.)\"\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result('system', command, match.group(1))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["tcch"] = {
    "telnet_command": "tcch",
    "action": tcch,
    "action_callback": tcch_callback_thread,
    "is_available": True
}


def shutdown():
    chrani_bot = __main__.chrani_bot
    command = "shutdown"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def shutdown_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "shutdown"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + "\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["shutdown"] = {
    "telnet_command": "shutdown",
    "action": shutdown,
    "action_callback": shutdown_callback_thread,
    "is_available": True
}


def lp():
    chrani_bot = __main__.chrani_bot
    command = "lp"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def lp_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "lp"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + r"\' by Telnet from (.*)([\s\S]+?)Total of (\d{1,2}) in the game", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            online_players_raw = match.group(2).lstrip()
            online_players_dict = {}
            for m in re.finditer(r"\d{1,2}. id=(\d+), (.+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(.*), ping=(\d+)\r\n", online_players_raw):
                online_players_dict.update({m.group(16): {
                    "entityid":         m.group(1),
                    "name":             str(m.group(2)),
                    "pos_x":            float(m.group(3)),
                    "pos_y":            float(m.group(4)),
                    "pos_z":            float(m.group(5)),
                    "rot_x":            float(m.group(6)),
                    "rot_y":            float(m.group(7)),
                    "rot_z":            float(m.group(8)),
                    "remote":           bool(m.group(9)),
                    "health":           int(m.group(10)),
                    "deaths":           int(m.group(11)),
                    "zombies":          int(m.group(12)),
                    "players":          int(m.group(13)),
                    "score":            m.group(14),
                    "level":            m.group(15),
                    "steamid":          m.group(16),
                    "ip":               str(m.group(17)),
                    "ping":             int(m.group(18)),
                    "is_online":        True,
                    "is_logging_in":    False
                }})

            common.set_active_action_result('system', command, online_players_dict)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["lp"] = {
    "telnet_command": "lp",
    "action": lp,
    "action_callback": lp_callback_thread,
    "is_available": True
}


def llp():
    chrani_bot = __main__.chrani_bot
    command = "llp"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting 'llp'")
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command 'llp' is active and waiting for a response!")


def llp_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "llp"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'llp\' by Telnet from (.*)([\s\S]+?)Total of (\d{1,3}) keystones in the game", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            lanclaims_raw = match.group(2)

            # I can't believe what a bitch this thing was. I tried no less than eight hours to find this crappy solution
            # re could not find a match whenever any form of unicode was present.  I've tried converting, i've tried string declarations,
            # I've tried flags. Something was always up. This is the only way i got this working.
            try:
                unicode(lanclaims_raw, "ascii")
            except UnicodeError:
                lanclaims_raw = unicode(lanclaims_raw, "utf-8")
            else:
                pass

            lcb_dict = {}
            # horrible, horrible way. But it works for now!
            for m in re.finditer(r"Player \"(?:.+)\((?P<player_steamid>\d+)\)\" owns \d+ keystones \(.+\)\s(?P<keystones>(\s+\(.+\)\s)+)", lanclaims_raw):
                keystones = re.findall(r"\((?P<pos_x>.\d{1,5}),\s(?P<pos_y>.\d{1,5}),\s(?P<pos_z>.\d{1,5})", m.group("keystones"))
                keystone_list = []
                for keystone in keystones:
                    keystone_list.append(keystone)

                lcb_dict.update({m.group("player_steamid"): keystone_list})

            common.set_active_action_result('system', command, lcb_dict)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["llp"] = {
    "telnet_command": "llp",
    "action": llp,
    "action_callback": llp_callback_thread,
    "is_available": True
}


def say(message, color=None):
    chrani_bot = __main__.chrani_bot
    command = "say"

    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    silent_mode = chrani_bot.settings.get_setting_by_name(name='silent_mode')
    if silent_mode:
        return True

    if color is None:
        color = chrani_bot.chat_colors['standard']

    try:
        chrani_bot.telnet_observer.tn.write("{command} \"[{color}]{message}[-]\"{line_end}".format(command=command, color=color, message=message, line_end=b"\r\n"))
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting 'say'")
    common.set_active_action_status('system', command, True)
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (message, color))


def say_callback_thread(message, color):
    chrani_bot = __main__.chrani_bot
    command = "say"
    poll_is_finished = False

    execution_time = time.time()
    while not poll_is_finished and not timeout_occurred(3, execution_time):
        logger.debug("waiting for response of 'say'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        try:
            for match in re.finditer(r"Executing command \'say \"\[" + color + "\]" + re.escape(message) + "\[-\]\"\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
                poll_is_finished = True
        except Exception as e:
            pass

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["say"] = {
    "telnet_command": "say",
    "action": say,
    "action_callback": say_callback_thread,
    "is_available": True
}


def saveworld():
    chrani_bot = __main__.chrani_bot
    command = "saveworld"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def saveworld_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "saveworld"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'saveworld\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["saveworld"] = {
    "telnet_command": "saveworld",
    "action": saveworld,
    "action_callback": saveworld_callback_thread,
    "is_available": True
}


def settime(timestring):
    chrani_bot = __main__.chrani_bot
    command = "settime"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {timestring} {line_end}".format(command=command, timestring=timestring, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (timestring, None))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def settime_callback_thread(timestring, dummy):
    chrani_bot = __main__.chrani_bot
    command = "settime"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + str(command) + " " + str(timestring) + "\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["settime"] = {
    "telnet_command": "settime",
    "action": settime,
    "action_callback": settime_callback_thread,
    "is_available": True
}


def bc_chatprefix():
    chrani_bot = __main__.chrani_bot
    command = "bc-chatprefix"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} \"/\"{line_end}".format(command=command, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def bc_chatprefix_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "bc-chatprefix"
    common.active_actions_dict[command] = True
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.actions_dict[command]["last_executed"]):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " \"/\"\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["bc-chatprefix"] = {
    "telnet_command": "bc-chatprefix",
    "action": bc_chatprefix,
    "action_callback": bc_chatprefix_callback_thread,
    "is_available": True
}


def removeentity(entity_id):
    chrani_bot = __main__.chrani_bot
    command = "removeentity"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {entity_id} {line_end}".format(command=command, entity_id=entity_id, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (entity_id, None))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def removeentity_callback_thread(entity_id, dummy):
    chrani_bot = __main__.chrani_bot
    command = "removeentity"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + str(command) + " " + str(entity_id) + "\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return poll_is_finished


common.actions_dict["removeentity"] = {
    "telnet_command": "removeentity",
    "action": removeentity,
    "action_callback": removeentity_callback_thread,
    "is_available": True
}


def debuffplayer(player_object, buff):
    chrani_bot = __main__.chrani_bot
    command = "debuffplayer"

    buff_list = [
        "bleeding",
        "foodPoisoning",
        "brokenLeg",
        "sprainedLeg"
    ]
    if buff not in buff_list:
        return False

    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    try:
        chrani_bot.telnet_observer.tn.write("{command} {player_steamid} {buff} {line_end}".format(command=command, player_steamid=player_object.steamid, buff=buff, line_end=b"\r\n"))
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting '{command}'".format(command=command))
    common.set_active_action_status('system', command, True)
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, buff))


def debuffplayer_callback_thread(player_object, buff):
    chrani_bot = __main__.chrani_bot
    command = "debuffplayer"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + str(command) + " " + str(player_object.steamid) + " " + str(buff) + "\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    return poll_is_finished


common.actions_dict["debuffplayer"] = {
    "telnet_command": "debuffplayer",
    "action": debuffplayer,
    "action_callback": debuffplayer_callback_thread,
    "is_available": True
}


def buffplayer(player_object, buff):
    chrani_bot = __main__.chrani_bot
    command = "buffplayer"

    buff_list = [
        "firstAidLarge"
    ]
    if buff not in buff_list:
        return False

    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {player_steamid} {buff} {line_end}".format(command=command, player_steamid=player_object.steamid, buff=buff, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, buff))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def buffplayer_callback_thread(player_object, buff):
    chrani_bot = __main__.chrani_bot
    command = "buffplayer"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed('system', command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + str(command) + " " + str(player_object.steamid) + " " + str(buff) + "\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result('system', command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return poll_is_finished


common.actions_dict["buffplayer"] = {
    "telnet_command": "buffplayer",
    "action": buffplayer,
    "action_callback": buffplayer_callback_thread,
    "is_available": True
}


"""
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
"""


def none():
    chrani_bot = __main__.chrani_bot
    command = "none"

    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    is_active = common.get_active_action_status('system', command)
    if not is_active:
        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status('system', command, True)
        logger.debug("waiting for response of '{command}'".format(command=command))
        common.set_active_action_result('system', command, "")
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status('system', command, False)
    return


common.actions_dict["none"] = {
    "telnet_command": "none",
    "action": none,
    "action_callback": None,
    "is_available": True
}
