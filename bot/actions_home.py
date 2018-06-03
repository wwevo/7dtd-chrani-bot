import re
from bot.location import Location
from bot.logger import logger

actions_home = []


def set_up_home(self):
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
                "leaving_core": "you are leaving {}\'s private area".format(player_object.name),
                "leaving_boundary": "you are leaving {}\'s estate".format(player_object.name),
                "entering_boundary": "you are entering {}\'s estate".format(player_object.name),
                "entering_core": "you are entering {}\'s private area".format(player_object.name)
            },
            shape='sphere',
            radius=10,
            warning_boundary=6,
            list_of_players_inside=[player_object.steamid]
        )
        location_object = Location(**location_dict)
        self.bot.locations.upsert(location_object, save=True)
        self.tn.say("{} has decided to settle down!".format(player_object.name), color=self.bot.chat_colors['background'])
        self.tn.send_message_to_player(player_object, "Home is where your hat is!", color=self.bot.chat_colors['success'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "add home",
        "usage" : "/add home"
    },
    "action" : set_up_home,
    "env": "(self)",
    "group": "home",
    "essential" : False
})


def remove_home(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            self.bot.locations.remove(player_object.steamid, 'home')

        except KeyError:
            self.tn.send_message_to_player(player_object, "I could not find your home. Did you set one up?", color=self.bot.chat_colors['warning'])
            raise KeyError

    except Exception as e:
        logger.error(e)
        return False

    self.tn.send_message_to_player(player_object, "Your home has been removed.", color=self.bot.chat_colors['warning'])

    return True


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "remove home",
        "usage" : "/remove home"
    },
    "action" : remove_home,
    "env": "(self)",
    "group": "home",
    "essential" : False
})


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


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit home teleport",
        "usage" : "/edit home teleport"
    },
    "action" : set_up_home_teleport,
    "env": "(self)",
    "group": "home",
    "essential" : False
})


def set_up_home_name(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"edit\shome\sname\s([\W\w\s]{1,19})$", command)
        if p:
            description = p.group(1)
            try:
                location_object = self.bot.locations.get(player_object.steamid, "home")

            except KeyError:
                self.tn.send_message_to_player(player_object, "{} can not name that which you do not have!".format(player_object.name), color=self.bot.chat_colors['warning'])
                raise KeyError

    except Exception as e:
        logger.error(e)
        return False

    location_object.set_description(description)
    messages_dict = {
        "leaving_core": "you are leaving {}\'s core".format(description),
        "leaving_boundary": "you are leaving {}".format(description),
        "entering_boundary": "you are entering {}".format(description),
        "entering_core": "you are entering {}\'s core".format(description)
    }
    location_object.set_messages(messages_dict)
    self.bot.locations.upsert(location_object, save=True)
    self.tn.send_message_to_player(player_object, "Your home is called {} now \o/".format(location_object.description), color=self.bot.chat_colors['background'])

    return True

actions_home.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "edit home name",
        "usage" : "/edit home name"
    },
    "action" : set_up_home_name,
    "env": "(self, command)",
    "group": "home",
    "essential" : False
})


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


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "take me home",
        "usage" : "/take me home"
    },
    "action" : take_me_home,
    "env": "(self)",
    "group": "home",
    "essential" : False
})


def goto_player_home(self, command):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        p = re.search(r"take\sme\sto\splayer\s(?P<steamid>([0-9]{17}))|(?P<entityid>[0-9]+)\shome", command)
        if p:
            player_steamid = p.group("steamid")
            player_entityid = p.group("entityid")
            if player_steamid is None:
                player_steamid = self.bot.players.entityid_to_steamid(player_entityid)
                if player_steamid is False:
                    raise KeyError
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


actions_home.append({
    "match_mode" : "startswith",
    "command" : {
        "trigger" : "take me to player",
        "usage" : "/take me to player <steamid/entityid> home"
    },
    "action" : goto_player_home,
    "env": "(self, command)",
    "group": "home",
    "essential" : False
})


def set_up_home_outer_perimeter(self):
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


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit home outer perimeter",
        "usage" : "/edit home outer perimeter"
    },
    "action" : set_up_home_outer_perimeter,
    "env": "(self)",
    "group": "home",
    "essential" : False
})


def set_up_home_inner_perimeter(self):
    try:
        player_object = self.bot.players.get(self.player_steamid)
        try:
            location_object = self.bot.locations.get(player_object.steamid, "home")
        except KeyError:
            self.tn.send_message_to_player(player_object, "coming from the wrong end... set up a home first!", color=self.bot.chat_colors['warning'])
            return False

        if location_object.set_warning_boundary(player_object):
            self.bot.locations.upsert(location_object, save=True)
            self.tn.send_message_to_player(player_object, "your private area ends here and spans {} meters ^^".format(int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['success'])
        else:
            self.tn.send_message_to_player(player_object, "you given range ({}) seems to be invalid ^^".format(int(location_object.warning_boundary * 2)), color=self.bot.chat_colors['warning'])
    except Exception as e:
        logger.error(e)
        pass


actions_home.append({
    "match_mode" : "isequal",
    "command" : {
        "trigger" : "edit home inner perimeter",
        "usage" : "/edit home inner perimeter"
    },
    "action" : set_up_home_inner_perimeter,
    "env": "(self)",
    "group": "home",
    "essential" : False
})
"""
here come the observers
"""
# no observers as of now
