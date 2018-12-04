import os
from bot.modules.logger import logger
from bot.assorted_functions import TimeoutError

schedulers_dict = {}
schedulers_controller = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module == 'common.py' or module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module


def run_schedulers(chrani_bot):
    command_queue = []
    for name, scheduler in chrani_bot.schedulers_dict.iteritems():
        if scheduler["type"] == 'schedule':  # we only want the monitors here, the player is active, no triggers needed
            scheduler_function_name = scheduler["action"]
            command_queue.append({
                "name": name,
                "scheduler": scheduler_function_name,
                "is_active": chrani_bot.schedulers_controller[name]["is_active"]
            })

    for command in command_queue:
        if command["is_active"]:
            try:
                result = command["scheduler"](chrani_bot)
            except TypeError as error:
                logger.debug("{} had a type error ({})".format(command["scheduler"], error.message))
                pass
            except AttributeError as error:
                logger.debug("{} had an attribute error! ({})".format(command["scheduler"], error.message))
                pass
            except IOError as error:
                logger.debug("{} had an input/output error! ({})".format(command["scheduler"], error.message))
                chrani_bot.has_connection = False
                pass
            except TimeoutError as error:
                logger.debug("{} had a timeout! ({})".format(command["scheduler"], error.message))
                pass
            except Exception as error:
                logger.error("{} had an unknown error! ({})".format(command["scheduler"], type(error)))
                pass
