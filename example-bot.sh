#!/bin/sh
pgrep -f "chrani-bot.py example-bot" || nohup python /opt/7dtd-chrani-bot/app/chrani-bot.py example-bot --verbosity=DEBUG &
