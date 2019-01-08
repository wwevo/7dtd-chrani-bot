#!/bin/sh
pgrep -f "chrani-bot.py chrani-bot_example" || . /opt/chrani-bot/venv_app/bin/activate && nohup python /opt/chrani-bot/app/chrani-bot.py chrani-bot_example --verbosity=DEBUG &
