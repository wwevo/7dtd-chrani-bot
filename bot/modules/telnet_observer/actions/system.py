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


def mem_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "mem"
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
        for match in re.finditer(chrani_bot.match_types_system["mem_status"], chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.active_actions_dict[command] = False
    return


common.actions_dict["mem"] = {
    "telnet_command": "mem",
    "last_executed": "0",
    "last_result": "",
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
        logger.debug("starting 'gt'")
        thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
    else:
        logger.debug("command 'gt' is active and waiting for a response!")


def gt_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "gt"
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
        for match in re.finditer(r"Day\s(\d{1,5}),\s(\d{1,2}):(\d{1,2}).*", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished 'gt'")
    common.active_actions_dict[command] = False
    return


common.actions_dict["gt"] = {
    "telnet_command": "gt",
    "last_executed": "0",
    "last_result": "",
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
        logger.debug("starting 'gg'")
        try:
            thread.start_new_thread(common.actions_dict[command]["action_callback"], ())
        except Exception as e:
            print(type(e))
    else:
        logger.debug("command 'gg' is active and waiting for a response!")


def gg_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "gg"

    common.active_actions_dict[command] = True
    common.actions_dict[command]["last_executed"] = time.time()
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(10, common.actions_dict[command]["last_executed"]):
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
            common.actions_dict[command]["last_result"] = match.group(2)
        time.sleep(0.5)

    logger.debug("finished 'gg'")
    common.active_actions_dict[command] = False
    return


common.actions_dict["gg"] = {
    "telnet_command": "gg",
    "last_executed": "0",
    "last_result": "",
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

    try:
        chrani_bot.telnet_observer.tn.write('{command} \"/\" {line_end}'.format(command=command, line_end=b"\r\n"))
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


def tcch_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "tcch"
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
        for match in re.finditer(r"Executing command \'" + command + "\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.active_actions_dict[command] = False
    return


common.actions_dict["tcch"] = {
    "telnet_command": "tcch",
    "last_executed": "0",
    "last_result": "",
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


def shutdown_callback_thread():
    chrani_bot = __main__.chrani_bot
    command = "shutdown"
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
        for match in re.finditer(r"Executing command \'" + command + "\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.actions_dict[command]["last_result"] = match.group(0)
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.active_actions_dict[command] = False
    return


common.actions_dict["shutdown"] = {
    "telnet_command": "shutdown",
    "last_executed": "0",
    "last_result": "",
    "action": shutdown,
    "action_callback": shutdown_callback_thread,
    "is_available": True
}
