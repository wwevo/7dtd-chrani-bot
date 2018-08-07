from bot.modules.logger import logger
import common


def mute_unauthenticated_player(self):
    if self.bot.settings.get_setting_by_name("mute_unauthenticated") is not True:
        return

    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        if player_object.authenticated is not True:
            if self.tn.muteplayerchat(player_object, True):
                self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.bot.chat_colors['warning'])
        else:
            if self.tn.muteplayerchat(player_object, False):
                self.tn.send_message_to_player(player_object, "Your chat has been enabled", color=self.bot.chat_colors['success'])

    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_player,
    "env": "(self)",
    "essential": True
})


def initialize_player(self):
    try:
        player_object = self.bot.players.get_by_steamid(self.player_steamid)
        player_moved_mouse = False

        if player_object.initialized is not True:
            if player_object.old_rot_x != player_object.rot_x:
                player_moved_mouse = True
            # if player_object.old_rot_y != player_object.rot_y:
            #     player_moved_mouse = True
            if player_object.old_rot_z != player_object.rot_z:
                player_moved_mouse = True

            if player_moved_mouse is True:
                player_object.initialized = True
                logger.debug("{} has been caught moving their head :)".format(player_object.name))
                return True

        return False
    except Exception as e:
        logger.exception(e)
        pass


common.observers_list.append({
    "type": "monitor",
    "title": "initialize player",
    "action": initialize_player,
    "env": "(self)",
    "essential": True
})