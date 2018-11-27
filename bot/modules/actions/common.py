import os
from bot.modules.logger import logger
from bot.assorted_functions import ResponseMessage


actions_list = []
observers_list = []

for module in os.listdir(os.path.dirname(__file__)):
    if module == 'common.py' or module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module


def find_action_help(key, value):
    for i, dic in enumerate(actions_list):
        if dic["group"] == key and dic["command"]["trigger"] == value:
            return dic["command"]["usage"]
    return None


def trigger_action(bot, source_player, target_player, command_parameters):
    command_queue = []
    if bot.actions_list is not None:
        denied = False
        for player_action in bot.actions_list:
            function_category = player_action["group"]
            function_name = getattr(player_action["action"], 'func_name')
            if (player_action["match_mode"] == "isequal" and player_action["command"]["trigger"] == command_parameters) or (player_action["match_mode"] == "startswith" and command_parameters.startswith(player_action["command"]["trigger"])):
                has_permission = bot.permissions.player_has_permission(source_player, function_name, function_category)
                if (isinstance(has_permission, bool) and has_permission is True) or (player_action["essential"] is True):
                    function_object = player_action["action"]
                    command_queue.append({
                        "action": function_object,
                        "func_name": function_name,
                        "group": function_category,
                        "command_parameters": command_parameters
                    })
                else:
                    denied = True
                    logger.info("Player {} denied trying to execute {}:{}".format(source_player.name, function_category, function_name))

        if len(command_queue) == 0:
            logger.debug("Player {} tried the command '/{}' for which I have no handler.".format(source_player.name, command_parameters))

        response_messages = ResponseMessage()
        if denied is True:
            message = "Access to this command is denied!"
            response_messages.add_message(message, False)
            bot.tn.send_message_to_player(source_player, message, color=bot.chat_colors['warning'])

        for command in command_queue:
            try:
                response = command["action"](bot, source_player, target_player, command["command_parameters"])
                if response is not False:
                    response_messages.add_message(command["func_name"], response.get_message_dict())
                    logger.info("Player {} has executed {}:{} with '/{}'".format(source_player.name, command["group"], command["func_name"], command["command_parameters"]))
            except ValueError as e:
                logger.debug("Player {} tried to execute {}:{} with '/{}', which led to: {}".format(source_player.name, command["group"], command["func_name"], command["command_parameters"], e.message))
            except Exception as e:
                logger.exception(e)

            bot.socketio.emit('command_log', {"steamid": source_player.steamid, "name": source_player.name, "command": "{}:{} = /{}".format(command["group"], command["func_name"],command["command_parameters"])}, namespace='/chrani-bot/public')

        return response_messages
