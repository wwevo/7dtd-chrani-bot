#!/bin/sh
pgrep -f "chrani-bot.py example-bot" || . /opt/example-bot/venv_pypy/bin/activate && nohup python /opt/example-bot/app/chrani-bot.py example-bot --verbosity=DEBUG &
