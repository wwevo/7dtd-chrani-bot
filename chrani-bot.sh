#!/bin/sh
pgrep -f chrani-bot.py || nohup python /opt/7dtd-chrani-bot/chrani-bot.py chrani-bot --verbosity=DEBUG &
