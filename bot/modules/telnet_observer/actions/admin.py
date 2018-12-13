import __main__
import common
import re
import time
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred

""" muting """


def mpc(player_object, status):
    chrani_bot = __main__.chrani_bot
    command = "mpc"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {steamid} {status} {line_end}".format(command=command, steamid=player_object.steamid, status=status, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, status))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def mpc_callback_thread(player_object, status):
    chrani_bot = __main__.chrani_bot
    command = "mpc"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " " + str(player_object.steamid) + " (True|False)\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["mpc"] = {
    "telnet_command": "mpc",
    "action": mpc,
    "action_callback": mpc_callback_thread,
    "is_available": True
}


def bc_mute(player_object, status):
    chrani_bot = __main__.chrani_bot
    command = "bc-mute"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {steamid} {status} {line_end}".format(command=command, steamid=player_object.steamid, status=status, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, status))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def bc_mute_callback_thread(player_object, status):
    chrani_bot = __main__.chrani_bot
    command = "bc-mute"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
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
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["bc-mute"] = {
    "telnet_command": "bc-mute",
    "action": bc_mute,
    "action_callback": bc_mute_callback_thread,
    "is_available": True
}


def kick(player_object, reason):
    chrani_bot = __main__.chrani_bot
    command = "kick"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            format_dict = {
                "command": command,
                "steamid": player_object.steamid,
                "reason": reason,
                "line_end": b"\r\n"
            }
            chrani_bot.telnet_observer.tn.write('{command} {steamid} "{reason}" {line_end}'.format(**format_dict))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, reason))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def kick_callback_thread(player_object, reason):
    chrani_bot = __main__.chrani_bot
    command = "kick"
    poll_is_finished = False
    time.sleep(0.5)

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " " + str(player_object.steamid) + " \"(.*)\"\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    player_object.is_about_to_be_kicked = False
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["kick"] = {
    "telnet_command": "kick",
    "action": kick,
    "action_callback": kick_callback_thread,
    "is_available": True
}


def ban(player_object, reason, duration_in_hours=None):
    chrani_bot = __main__.chrani_bot
    command = "ban"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            format_dict = {
                "command": command,
                "steamid": player_object.steamid,
                "duration": duration_in_hours,
                "reason": reason,
                "line_end": b"\r\n"
            }
            chrani_bot.telnet_observer.tn.write('{command} {steamid} {duration} hours "{reason}" {line_end}'.format(**format_dict))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, reason, duration_in_hours))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def ban_callback_thread(player_object, reason, duration_in_hours):
    chrani_bot = __main__.chrani_bot
    command = "ban"
    poll_is_finished = False
    time.sleep(0.5)

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " " + str(player_object.steamid) + " \"" + reason + "\"\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["ban"] = {
    "telnet_command": "ban",
    "action": ban,
    "action_callback": ban_callback_thread,
    "is_available": True
}


def unban(player_object):
    chrani_bot = __main__.chrani_bot
    command = "unban"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            format_dict = {
                "command": command,
                "steamid": player_object.steamid,
                "line_end": b"\r\n"
            }
            chrani_bot.telnet_observer.tn.write('{command} remove {steamid} {line_end}'.format(**format_dict))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{command}'".format(command=command))
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, None))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def unban_callback_thread(player_object, dummy):
    chrani_bot = __main__.chrani_bot
    command = "unban"
    poll_is_finished = False
    time.sleep(0.5)

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of '{command}'".format(command=command))
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'" + command + " " + str(player_object.steamid) + "\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(0))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["unban"] = {
    "telnet_command": "unban",
    "action": unban,
    "action_callback": unban_callback_thread,
    "is_available": True
}
