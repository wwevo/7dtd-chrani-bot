import __main__
import common
import re
import time
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def lpf(player_object):
    chrani_bot = __main__.chrani_bot
    command = "lpf"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    try:
        chrani_bot.telnet_observer.tn.write("{command} {steamid} {line_end}".format(command=command, steamid=player_object.steamid, line_end=b"\r\n"))
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting 'lpf'")
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, None))


def lpf_callback_thread(player_object, dummy):
    chrani_bot = __main__.chrani_bot
    command = "lpf"
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.actions_dict[command]["last_executed"]):
        logger.debug("waiting for response of 'lpf'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'lpf " + str(player_object.steamid) + "\' by Telnet from (.*)([\s\S]+?)FriendsOf id=" + str(player_object.steamid) + ", friends=(?P<friendslist>.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group("friendslist")
        time.sleep(0.5)

    logger.debug("finished 'lpf'")
    return


common.actions_dict["lpf"] = {
    "telnet_command": "lpf",
    "last_executed": "0",
    "last_result": "",
    "action": lpf,
    "action_callback": lpf_callback_thread,
    "is_available": True
}


def lp():
    chrani_bot = __main__.chrani_bot
    command = "lp"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    try:
        chrani_bot.telnet_observer.tn.write("{command} {line_end}".format(command=command, line_end=b"\r\n"))
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    try:
        is_active = common.active_actions_dict[command]
    except KeyError:
        is_active = False

    if not is_active:
        logger.debug("starting '{command}'".format(command=command))
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def lp_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "lp"
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
        for match in re.finditer(r"Executing command \'" + command + "\' by Telnet from (.*)([\s\S]+?)Total of (\d{1,2}) in the game", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(2)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.active_actions_dict[command] = False
    return


common.actions_dict["lp"] = {
    "telnet_command": "lp",
    "last_executed": "0",
    "last_result": "",
    "action": lp,
    "action_callback": lp_callback_thread,
    "is_available": True
}
