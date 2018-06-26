from bot.logger import logger
import re

actions_players = []


def teleport_self_to_player(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"goto\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
        if p:
            steamid_to_teleport_to = p.group("steamid")
            entityid_to_teleport_to = p.group("entityid")
            if steamid_to_teleport_to is None:
                steamid_to_teleport_to = self.bot.players.entityid_to_steamid(entityid_to_teleport_to)
                if steamid_to_teleport_to is False:
                    self.tn.send_message_to_player(player_object, "could not find player", color=self.bot.chat_colors['error'])
                    return False
            if int(steamid_to_teleport_to) == int(player_object.steamid):
                self.tn.send_message_to_player(player_object, "Try meditation, if you want to find yourself ^^", color=self.bot.chat_colors['warning'])
                return False
            else:
                player_object_to_teleport_to = self.bot.players.get(steamid_to_teleport_to)
        else:
            self.tn.send_message_to_player(player_object, "you did not specify a player. Use {}".format(self.bot.find_action_help("players", "goto player")), color=self.bot.chat_colors['warning'])
            return False

    except Exception as e:
        logger.exception(e)
        raise KeyError

    coord_tuple = (player_object_to_teleport_to.pos_x, player_object_to_teleport_to.pos_y, player_object_to_teleport_to.pos_z)
    if self.tn.teleportplayer(player_object, coord_tuple=coord_tuple):
        self.tn.send_message_to_player(player_object, "You have been ported to {}'s last known location".format(player_object_to_teleport_to.name), color=self.bot.chat_colors['success'])
    else:
        self.tn.send_message_to_player(player_object, "Teleporting to player {} failed :(".format(player_object_to_teleport_to.name), color=self.bot.chat_colors['error'])
    return True


actions_players.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "goto player",
        "usage" : "/goto player <steamid/entityid>"
    },
    "action" : teleport_self_to_player,
    "env": "(self, command)",
    "group": "players",
    "essential" : False
})


def teleport_player_to_self(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"summon\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)", command)
        if p:
            steamid_to_fetch = p.group("steamid")
            entityid_to_fetch = p.group("entityid")
            if steamid_to_fetch is None:
                steamid_to_fetch = self.bot.players.entityid_to_steamid(entityid_to_fetch)
                if steamid_to_fetch is False:
                    self.tn.send_message_to_player(player_object, "could not find player", color=self.bot.chat_colors['error'])
                    return False
            if int(steamid_to_fetch) == int(player_object.steamid):
                self.tn.send_message_to_player(player_object, "Hands off those drugs man. They ain't good for you!", color=self.bot.chat_colors['warning'])
                return False
            else:
                player_object_to_teleport_to = self.bot.players.get(steamid_to_fetch)
        else:
            self.tn.send_message_to_player(player_object, "you did not specify a player. Use {}".format(self.bot.find_action_help("players", "summon player")), color=self.bot.chat_colors['warning'])
            return False

    except Exception as e:
        logger.exception(e)
        raise KeyError

    coord_tuple = (player_object_to_teleport_to.pos_x, player_object_to_teleport_to.pos_y, player_object_to_teleport_to.pos_z)
    if self.tn.teleportplayer(player_object, coord_tuple=coord_tuple):
        self.tn.send_message_to_player(player_object, "You have been summoned to {}'s location".format(player_object_to_teleport_to.name), color=self.bot.chat_colors['success'])
    else:
        self.tn.send_message_to_player(player_object, "Summoning player {} failed :(".format(player_object_to_teleport_to.name), color=self.bot.chat_colors['error'])
    return True


actions_players.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "summon player",
        "usage" : "/summon player <steamid/entityid>"
    },
    "action" : teleport_player_to_self,
    "env": "(self, command)",
    "group": "players",
    "essential" : False
})
