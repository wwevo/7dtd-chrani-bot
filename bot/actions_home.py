import re
from bot.location import Location
from bot.logger import logger

actions_home = []


def make_this_my_home(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        # if you know what you are doing, yuo can circumvent all checks and set up a location by dictionary
        location_dict = dict(
            name='My Home',
            identifier='home',
            owner=player_object.steamid,
            pos_x=player_object.pos_x,
            pos_y=player_object.pos_y,
            pos_z=player_object.pos_z,
            tele_x=player_object.pos_x,
            tele_y=player_object.pos_y,
            tele_z=player_object.pos_z,
            description="{}\'s home".format(player_object.name),
            messages_dict={
                "leaving_core": None,
                "leaving_boundary": "you are leaving {}\'s estate".format(player_object.name),
                "entering_boundary": "you are entering {}\'s estate".format(player_object.name),
                "entering_core": None
            },
            shape='sphere',
            radius=10,
            warning_boundary=6,
            region=[player_object.region],
            list_of_players_inside=[player_object.steamid]
        )
        location_object = Location(**location_dict)
        self.bot.locations.upsert(location_object, save=True)
        self.tn.say("{} has decided to settle down!".format(player_object.name), color=self.bot.chat_colors['background'])
        self.tn.send_message_to_player(player_object, "Home is where your hat is!", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("isequal", "set home", make_this_my_home, "(self)", "home"))


def set_up_home_teleport(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "home")
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_teleport_coordinates(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "your teleport has been set up!", color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "your position seems to be outside your home", color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("isequal", "set home teleport", set_up_home_teleport, "(self)", "home"))


def name_my_home(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"set\shome\sname\s([\w\s]{1,19})$", command)
        if p:
            description = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, "home")
                location_object.set_description(description)
                self.bot.locations.upsert(location_object, save=True)
                self.tn.send_message_to_player(player_object, "Your home is called {} now \o/".format(location_object.description), color=self.bot.chat_colors['background'])
                return True

            except KeyError:
                self.tn.send_message_to_player(player_object, "{} can not name that which you do not have!".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("startswith", "set home name", name_my_home, "(self, command)", "home"))


def take_me_home(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "home")
            if location_object.player_is_inside_boundary(player_object):
                self.tn.send_message_to_player(player_object, "eh, you already ARE home oO".format(player_object.name), color=self.bot.chat_colors['warning'])
            else:
                self.tn.teleportplayer(player_object, location_object)
                self.tn.say("{} got homesick".format(player_object.name), color=self.bot.chat_colors['background'])
        except KeyError:
            self.tn.send_message_to_player(player_object, "You seem to be homeless".format(player_object.name), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("isequal", "take me home", take_me_home, "(self)", "home"))


def goto_playerhome(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"goto\shome\s(.+)", command)
        if p:
            player_steamid = p.group(1)
            try:
                player_object_to_port_to = self.bot.players.load(player_steamid)
                location_object = self.bot.locations.get(player_object_to_port_to.steamid, "home")
                self.tn.teleportplayer(player_object, location_object)
                self.tn.send_message_to_player(player_object, "You went to visit {}'s home".format(player_object_to_port_to.name), color=self.bot.chat_colors['background'])
                self.tn.send_message_to_player(player_object_to_port_to, "{} went to visit your home!".format(player_object.name), color=self.bot.chat_colors['warning'])
            except KeyError:
                self.tn.send_message_to_player(player_object, "Could not find {}'s home".format(player_steamid), color=self.bot.chat_colors['warning'])
                pass
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("startswith", "goto home", goto_playerhome, "(self, command)", "home"))


def set_up_home_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "home")
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_radius(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "your estate ends here and spans {} meters ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.radius * 2)), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("isequal", "set home inner perimeter", set_up_home_perimeter, "(self)", "home"))


def set_up_home_warning_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "home")
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_warning_boundary(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "your private area ends here and spans {} meters ^^".format(int(location_object.boundary_radius * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.boundary_radius * 2)), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append(("isequal", "set home outer perimeter", set_up_home_warning_perimeter, "(self)", "home"))


# def make_my_home_a_shape(self, command):
#     try:
#         player_object = self.bot.players.get(self.player_steamid)
#         p = re.search(r"make\smy\shome\sa\s(.+)", command)
#         if p:
#             shape = p.group(1)
#             try:
#                 location_object = self.bot.locations.get(player_object.steamid, "home")
#                 if location_object.set_shape(shape):
#                     self.bot.locations.upsert(location_object, save=True)
#                     self.tn.send_message_to_player(player_object, "{}'s home is a {} now.".format(player_object.name, shape), color=self.bot.chat_colors['success'])
#                     return True
#                 else:
#                     self.tn.send_message_to_player(player_object, "{} is not an allowed shape at this time!".format(shape), color=self.bot.chat_colors['warning'])
#                     return False
#
#             except KeyError:
#                 self.tn.send_message_to_player(player_object, "{} can not change that which you do not own!!".format(player_object.name), color=self.bot.chat_colors['warning'])
#     except Exception as e:
#         logger.error(e)
#         pass
#
#
# actions_home.append(("startswith", "make my home a", make_my_home_a_shape, "(self, command)", "home"))


"""
here come the observers
"""
# no observers, they are all generic and found in actions_locations
