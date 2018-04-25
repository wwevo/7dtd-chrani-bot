#!/bin/sh
pgrep -f 7dtd-chrani-bot.py || python /opt/7dtd-chrani-bot/chrani-bot.py bot_testing --verbosity=DEBUG
