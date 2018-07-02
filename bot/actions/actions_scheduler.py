from bot.modules.logger import logger

observers_scheduler = []


def mute_unauthenticated_player(self):
    if self.bot.settings_dict["mute_unauthenticated"] is not True:
        return

    try:
        player_object = self.bot.players.get(self.player_steamid)
        if player_object.authenticated is not True:
            if self.tn.muteplayerchat(player_object, True):
                self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
        else:
            if self.tn.muteplayerchat(player_object, False):
                self.tn.send_message_to_player(player_object, "Your chat has been enabled", color=self.bot.chat_colors['success'])

    except Exception as e:
        logger.exception(e)
        pass


observers_scheduler.append({
    "type": "monitor",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_player,
    "env": "(self)",
    "essential" : True
})


def initialize_player(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        if player_object.old_rot_x != player_object.rot_x:
            player_object.initialized = True
        if player_object.old_rot_y != player_object.rot_y:
            player_object.initialized = True
        if player_object.old_rot_z != player_object.rot_z:
            player_object.initialized = True

    except Exception as e:
        logger.exception(e)
        pass


observers_scheduler.append({
    "type": "monitor",
    "title": "initialize player",
    "action": initialize_player,
    "env": "(self)",
    "essential" : True
})
