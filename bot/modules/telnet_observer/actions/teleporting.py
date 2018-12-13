import __main__
import common
import re
import time
import math
import thread
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def teleportplayer(player_object, location_object=None, coord_tuple=None):
    chrani_bot = __main__.chrani_bot
    command = "teleportplayer"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        if not player_object.is_online:
            return False

        common.active_actions_dict[command] = True

        if location_object is not None:
            try:
                coord_tuple = (int(math.ceil(float(location_object.tele_x))), int(math.ceil(float(location_object.tele_y))), int(math.ceil(float(location_object.tele_z))))
            except:
                coord_tuple = (int(math.ceil(float(location_object.pos_x))), int(math.ceil(float(location_object.pos_y))), int(math.ceil(float(location_object.pos_z))))
        else:
            try:
                coord_tuple = (int(math.ceil(float(coord_tuple[0]))), int(math.ceil(float(coord_tuple[1]))), int(math.ceil(float(coord_tuple[2]))))
            except:
                return False

        if not player_object.is_responsive():
            return False

        player_object.set_last_teleport()
        player_object.pos_x = coord_tuple[0]
        player_object.pos_y = coord_tuple[1]
        player_object.pos_z = coord_tuple[2]
        chrani_bot.players.upsert(player_object)

        try:
            chrani_bot.telnet_observer.tn.write("{command} {player_steamid} {pos_x} {pos_y} {pos_z} {line_end}".format(command=command, player_steamid=player_object.steamid, pos_x=coord_tuple[0], pos_y=coord_tuple[1], pos_z=coord_tuple[2], line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting 'teleportplayer'")
        common.set_active_action_status(player_object.steamid, command, True)
        thread.start_new_thread(common.actions_dict[command]["action_callback"], (player_object, location_object, coord_tuple))
    else:
        logger.debug("command 'teleportplayer' is active and waiting for a response!")


def teleportplayer_callback_thread(player_object, location_object, coord_tuple):
    chrani_bot = __main__.chrani_bot
    command = "teleportplayer"
    poll_is_finished = False

    while not poll_is_finished and not timeout_occurred(5, common.get_active_action_last_executed(player_object.steamid, command)):
        logger.debug("waiting for response of 'teleportplayer'")
        m = re.search(r"\*\*\* ERROR: unknown command \'{command}\'".format(command=command), chrani_bot.telnet_observer.telnet_buffer)
        if m:
            logger.debug("command not recognized: {command}".format(command=command))
            common.actions_dict[command]["is_available"] = False
            poll_is_finished = True
            continue

        match = False
        for match in re.finditer(r"Executing command \'teleportplayer " + player_object.steamid + " (.*)\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True
            pass

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(2))
        time.sleep(0.5)

    logger.debug("finished '{command}'".format(command=command))
    common.set_active_action_status(player_object.steamid, command, False)
    return


common.actions_dict["teleportplayer"] = {
    "telnet_command": "teleportplayer",
    "action": teleportplayer,
    "action_callback": teleportplayer_callback_thread,
    "is_available": True
}
