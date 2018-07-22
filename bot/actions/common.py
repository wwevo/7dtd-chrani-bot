import os


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


