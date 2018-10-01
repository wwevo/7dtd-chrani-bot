#!/bin/sh
# pgrep -f "chrani-bot.py chrani-bot" || . /opt/7dtd-chrani-bot/venv_pypy/bin/activate && nohup python /opt/7dtd-chrani-bot/app/chrani-bot.py chrani-bot --verbosity=DEBUG &
pgrep -f "chrani-bot.py chrani-bot" || . /opt/7dtd-chrani-bot/venv_app/chrani-bot/bin/activate && nohup python /opt/7dtd-chrani-bot/app/chrani-bot.py chrani-bot --verbosity=DEBUG &