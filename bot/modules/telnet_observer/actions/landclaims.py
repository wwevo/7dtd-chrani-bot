import __main__
import common
import re
import time
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def llp():
    chrani_bot = __main__.chrani_bot
    command = "llp"
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
        logger.debug("starting 'llp'")
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command 'llp' is active and waiting for a response!")


def llp_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "llp"
    common.active_actions_dict[command] = True
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.actions_dict[command]["last_executed"]):
        logger.debug("waiting for response of 'llp'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'llp\' by Telnet from (.*)([\s\S]+?)Total of (\d{1,3}) keystones in the game", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(2)
        time.sleep(0.5)

    logger.debug("finished 'llp'")
    common.active_actions_dict[command] = False
    return


common.actions_dict["llp"] = {
    "telnet_command": "llp",
    "last_executed": "0",
    "last_result": "",
    "action": llp,
    "action_callback": llp_callback_thread,
    "is_available": True
}
