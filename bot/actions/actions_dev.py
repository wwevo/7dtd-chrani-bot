from bot.modules.logger import logger

actions_dev = []


def fix_players_legs(self):
    """Fixes the legs of the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /fix my legs please

    example:
    /fix my legs please

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.debuffplayer(player_object, "brokenLeg")
        self.tn.debuffplayer(player_object, "sprainedLeg")
        self.tn.send_message_to_player(player_object, "your legs have been taken care of ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "fix my legs please",
        "usage" : "/fix my legs please"
    },
    "action" : fix_players_legs,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def stop_the_bleeding(self):
    """Removes the 'bleeding' buff from the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /make me stop leaking

    example:
    /make me stop leaking

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.debuffplayer(player_object, "bleeding")
        self.tn.send_message_to_player(player_object, "your wounds have been bandaided ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "make me stop leaking",
        "usage" : "/make me stop leaking"
    },
    "action" : stop_the_bleeding,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def apply_first_aid(self):
    """Applies the 'firstAidLarge' buff to the player issuing this action

    Keyword arguments:
    self -- the bot

    expected bot command:
    /heal me up scotty

    example:
    /heal me up scotty

    notes:
    does not check if the player is injured at all
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.buffplayer(player_object, "firstAidLarge")
        self.tn.send_message_to_player(player_object, "feel the power flowing through you!! ^^", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "heal me up scotty",
        "usage" : "/heal me up scotty"
    },
    "action" : apply_first_aid,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def reload_from_db(self):
    """Reloads config and location files from storage

    Keyword arguments:
    self -- the bot

    expected bot command:
    /reinitialize

    example:
    /reinitialize
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.bot.load_from_db()
        self.tn.send_message_to_player(player_object, "loaded all from storage!", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.exception(e)
        pass


actions_dev.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "reinitialize",
        "usage" : "/reinitialize"
    },
    "action" : reload_from_db,
    "env": "(self)",
    "group": "testing",
    "essential" : False
})


def shutdown_bot(self):
    """Shuts down the bot

    Keyword arguments:
    self -- the bot

    expected bot command:
    /shut down the matrix

    example:
    /shut down the matrix

    notes:
    Together with a cronjob starting the bot every minute, this can be
    used for restarting it from within the game
    """
    try:
        player_object = self.bot.players.get(self.player_steamid)
        self.tn.send_message_to_player(player_object, "bot is shutting down...", color=self.bot.chat_colors['success'])
        self.bot.shutdown_bot()
    except Exception as e:
        logger.exception(e)
        pass


actions_dev.append({
    "match_mode": "isequal",
    "command": {
        "trigger": "shut down the matrix",
        "usage": "/shut down the matrix"
    },
    "action": shutdown_bot,
    "env": "(self)",
    "group": "testing",
    "essential": False
})
""" 
here come the observers
"""
