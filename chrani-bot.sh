#!/bin/sh
pgrep -f chrani-bot.py || nohup python /opt/7dtd-chrani-bot/chrani-bot.py bot_testing --verbosity=DEBUG &
