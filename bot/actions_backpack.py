from bot.logger import logger

actions_backpack = []


def take_me_to_my_backpack(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "death")
            if location_object.player_is_inside_boundary(player_object):
                self.tn.send_message_to_player(player_object, "eh, you already ARE near your pack oO".format(player_object.name), color=self.bot.chat_colors['warning'])
            else:
                self.tn.teleportplayer(player_object, location_object)
                self.tn.say("{} can't live without their stuff".format(player_object.name), color=self.bot.chat_colors['background'])

            self.bot.locations.remove(player_object.steamid, 'death')

        except KeyError:
            self.tn.send_message_to_player(player_object, "I don't have your last death on record, sorry :(".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_backpack.append(("isequal", "take me to my pack", take_me_to_my_backpack, "(self)", "backpack"))


