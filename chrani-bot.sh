#!/bin/sh
pgrep -f "chrani-bot.py chrani-bot" || nohup python /opt/7dtd-chrani-bot/app/chrani-bot.py chrani-bot --verbosity=DEBUG &
