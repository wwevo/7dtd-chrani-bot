import __main__
import common
import re
import time
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def pm(player_object, message, color=None):
    chrani_bot = __main__.chrani_bot
    command = "pm"

    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return

    if not player_object.is_online:
        return False

    silent_mode = chrani_bot.settings.get_setting_by_name(name='silent_mode')
    if silent_mode:
        return True

    if color is None:
        color = chrani_bot.chat_colors['standard']

    try:
        command = "{command} {steamid} \"[{color}]{message}[-]\"{line_end}".format(command=command, steamid=player_object.steamid, color=color, message=message, line_end=b"\r\n")
        chrani_bot.telnet_observer.tn.write(command)
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting 'pm'")
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, message, color))


def pm_callback_thread(player_object, message, color):
    chrani_bot = __main__.chrani_bot
    command = "pm"
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.actions_dict[command]["last_executed"]):
        logger.debug("waiting for response of 'pm'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'pm\' " + str(player_object.steamid) + " \"[{color}]" + message + "[-]\" by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished 'pm'")
    return


common.actions_dict["pm"] = {
    "telnet_command": "pm",
    "last_executed": "0",
    "last_result": "",
    "action": pm,
    "action_callback": pm_callback_thread,
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
        command = "{command} \"[{color}]{message}[-]\"{line_end}".format(command=command, color=color, message=message, line_end=b"\r\n")
        chrani_bot.telnet_observer.tn.write(command)
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting 'say'")
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (message, color))


def say_callback_thread(message, color):
    chrani_bot = __main__.chrani_bot
    command = "say"
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(5, common.actions_dict[command]["last_executed"]):
        logger.debug("waiting for response of 'say'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'say\' \"[{color}]" + message + "[-]\" by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished 'say'")
    return


common.actions_dict["say"] = {
    "telnet_command": "say",
    "last_executed": "0",
    "last_result": "",
    "action": say,
    "action_callback": say_callback_thread,
    "is_available": True
}
