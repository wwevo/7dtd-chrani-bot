from bot.modules.logger import logger
import common


def mute_unauthenticated_player(self, player_object=None):
    if player_object.authenticated is not True:
        if self.tn.muteplayerchat(player_object, True):
            self.tn.send_message_to_player(player_object, "Your chat has been disabled!", color=self.chat_colors['warning'])
    else:
        if self.tn.muteplayerchat(player_object, False):
            self.tn.send_message_to_player(player_object, "Your chat has been enabled", color=self.chat_colors['success'])


common.observers_list.append({
    "type": "trigger",
    "title": "mute unauthenticated players",
    "action": mute_unauthenticated_player,
    "env": "(self, player_object)",
    "essential": True
})


def initialize_player(self):
    if self.player_object.initialized is not True:
        player_moved_mouse = False
        if self.player_object.old_rot_x != self.player_object.rot_x:
            player_moved_mouse = True
        # if player_object.old_rot_y != player_object.rot_y:
        #     player_moved_mouse = True
        if self.player_object.old_rot_z != self.player_object.rot_z:
            player_moved_mouse = True

        if player_moved_mouse is True:
            self.player_object.initialized = True
            logger.debug("{} has been caught moving their head :)".format(self.player_object.name))
            return True

    return False


common.observers_list.append({
    "type": "monitor",
    "title": "initialize player",
    "action": initialize_player,
    "env": "(self)",
    "essential": True
})
