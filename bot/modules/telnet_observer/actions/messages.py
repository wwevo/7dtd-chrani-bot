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
        color = chrani_bot.dom["bot_data"]["settings"]["color_scheme"]['standard']

    try:
        chrani_bot.telnet_observer.tn.write("{command} {steamid} \"[{color}]{message}[-]\"{line_end}".format(command=command, steamid=player_object.steamid, color=color, message=message, line_end=b"\r\n"))
    except Exception as e:
        log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
        logger.error(log_message)
        raise IOError(log_message)

    logger.debug("starting 'pm'")
    common.set_active_action_status(player_object.steamid, command, True)
    thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, message, color))


def pm_callback_thread(player_object, message, color):
    chrani_bot = __main__.chrani_bot
    command = "pm"
    poll_is_finished = False

    execution_time = time.time()
    while not poll_is_finished and not timeout_occurred(3, execution_time):
        logger.debug("waiting for response of 'pm'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'pm " + str(player_object.steamid) + " \"[" + color + "]" + re.escape(message) + "[-]\"\' by Telnet from (.*)\r\n", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["pm"] = {
    "telnet_command": "pm",
    "action": pm,
    "action_callback": pm_callback_thread,
    "is_available": True
}
