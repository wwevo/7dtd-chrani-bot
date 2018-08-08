import os
from bot.modules.logger import logger


actions_list = []

for module in os.listdir(os.path.dirname(__file__)):
    if module in ['common.py', '__init__.py', 'webinterface.py'] or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())

    del module
