#!/bin/sh
pgrep -f "chrani-bot.py example-bot" || . /opt/chrani-bot/venv_pypy/bin/activate && nohup python /opt/chrani-bot/app/chrani-bot.py example-bot --verbosity=DEBUG &
