import os

actions_dict = {}
active_actions_dict = {}
action_results_dict = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module == 'common.py' or module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module


def trigger_action(bot, action, *args, **kwargs):
    try:
        if len(args) == 0:
            return actions_dict[action]["action"]()
        elif len(args) >= 1:
            return actions_dict[action]["action"](*args, **kwargs)
    except:
        pass
