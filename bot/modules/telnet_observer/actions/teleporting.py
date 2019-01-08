import __main__
import common
import re
import time
import math
import threading
from bot.modules.logger import logger
from bot.assorted_functions import timeout_occurred


def teleportplayer(player_object, location_object=None, coord_tuple=None, delay=None):
    chrani_bot = __main__.chrani_bot
    command = "teleportplayer"
    if not common.actions_dict[command]["is_available"]:
        time.sleep(1)
        return False

    is_active = common.get_active_action_status(player_object.steamid, command)
    if not is_active:
        if not chrani_bot.dom.get("bot_data").get("player_data").get(player_object.steamid).get("is_online"):
            return False

        if location_object is not None:
            try:
                target_tuple = (int(math.ceil(float(location_object.tele_x))), int(math.ceil(float(location_object.tele_y))), int(math.ceil(float(location_object.tele_z))))
            except:
                target_tuple = (int(math.ceil(float(location_object.pos_x))), int(math.ceil(float(location_object.pos_y))), int(math.ceil(float(location_object.pos_z))))
        else:
            try:
                target_tuple = (int(math.ceil(float(coord_tuple[0]))), int(math.ceil(float(coord_tuple[1]))), int(math.ceil(float(coord_tuple[2]))))
            except:
                return False

        if not player_object.is_responsive():
            return False

        chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["positional_data_timestamp"] = time.time()
        if target_tuple[0] == int(math.ceil(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"])) and target_tuple[2] == int(math.ceil(chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"])):
            print("you are already there, you just don't know it yet")
            return False
        else:
            common.set_active_action_status(player_object.steamid, command, True)
            try:
                if delay is not None:
                    message = "You will be ported to {location_name} in {seconds} seconds".format(location_name=location_object.name, seconds=delay)
                else:
                    delay = 0
                    message = "You will be ported to {location_name}".format(location_name=location_object.name)
            except Exception:
                delay = 0
                message = "You will be ported to some coordinates ({pos_x} {pos_y} {pos_z})".format(pos_x=target_tuple[0], pos_y=target_tuple[1], pos_z=target_tuple[2])
                pass

            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "pm", player_object, message, chrani_bot.dom.get("bot_data").get("settings").get("color_scheme").get("warning"))
            time.sleep(delay + 1)

        try:
            chrani_bot.telnet_observer.tn.write("{command} {player_steamid} {pos_x} {pos_y} {pos_z} {line_end}".format(command=command, player_steamid=player_object.steamid, pos_x=target_tuple[0], pos_y=target_tuple[1], pos_z=target_tuple[2], line_end=b"\r\n"))
        except Exception as e:
            log_message = 'trying to {command} on telnet connection failed: {error} / {error_type}'.format(command=command, error=e, error_type=type(e))
            logger.error(log_message)
            raise IOError(log_message)

        logger.debug("starting '{}'".format(command))
        worker_thread = threading.Thread(target=common.actions_dict[command]["action_callback"], args=(player_object, location_object, coord_tuple), name=command)
        worker_thread.start()
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
        for match in re.finditer(r"Executing command \'teleportplayer " + str(player_object.steamid) + " (.*)\' by Telnet from (.*)", chrani_bot.telnet_observer.telnet_buffer):
            poll_is_finished = True

        if match:
            common.set_active_action_result(player_object.steamid, command, match.group(1))
            if location_object is None:
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"] = coord_tuple[0]
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"] = coord_tuple[1]
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"] = coord_tuple[2]
            else:
                coord_tuple = location_object.get_teleport_coords_tuple()
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_x"] = coord_tuple[0]
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_y"] = coord_tuple[1]
                chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["pos_z"] = coord_tuple[2]

            chrani_bot.dom["bot_data"]["player_data"][player_object.steamid]["positional_data_timestamp"] = time.time()

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
