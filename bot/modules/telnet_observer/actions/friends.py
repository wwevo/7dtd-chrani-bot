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

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        try:
            chrani_bot.telnet_observer.tn.write("{command} {steamid} {line_end}".format(command=command, steamid=player_object.steamid, line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting 'lpf'")
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, None))
    else:
        logger.debug("command '{command}' is active and waiting for a response!".format(command=command))


def lpf_callback_thread(player_object, dummy):
    chrani_bot = __main__.chrani_bot
    command = "lpf"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(3, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of 'lpf'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'lpf " + str(player_object.steamid) + r"\' by Telnet from (.*)([\s\S]+?)FriendsOf id=" + str(player_object.steamid) + r", friends=(?P<friendslist>.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            friendslist_raw = match.group("friendslist").lstrip()
            if len(friendslist_raw) >= 1:
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["friends"] = friendslist_raw.split(',')

            common.set_active_action_result(player_object.steamid, command, match.group("friendslist"))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["lpf"] = {
    "telnet_command": "lpf",
    "action": lpf,
    "action_callback": lpf_callback_thread,
    "is_available": True
}
