actions_dev = []


def fix_players_legs(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        self.tn.debuffplayer(player_object, "brokenLeg")
        self.tn.debuffplayer(player_object, "sprainedLeg")
        self.tn.send_message_to_player(player_object, "your legs have been taken care of ^^", color='22c927')
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "fix my legs please", fix_players_legs, "(self)", "testing"))


def stop_the_bleeding(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        self.tn.debuffplayer(player_object, "bleeding")
        self.tn.send_message_to_player(player_object, "your wounds have been bandaided ^^", color='22c927')
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "make me stop leaking", stop_the_bleeding, "(self)", "testing"))


def apply_first_aid(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        self.tn.buffplayer(player_object, "firstAidLarge")
        self.tn.send_message_to_player(player_object, "feel the power flowing through you!! ^^", color='22c927')
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "heal me up scotty", apply_first_aid, "(self)", "testing"))


def make_player_admin(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        self.tn.set_admin_level(player_object, "2")
        self.tn.send_message_to_player(player_object, "and He said 'Let there be unlimited POWER!'. hit F1 and type cm <enter>, dm <enter>. exit console. press 'q' to fly, 'u' for items.", color='22c927')
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "make me all powerful!", make_player_admin, "(self)", "testing"))


def reload_from_db(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        try:
            self.bot.load_from_db()
            self.tn.send_message_to_player(player_object, "loaded all from storage!", color='22c927')
        except IOError:
            pass
    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "reinitialize", reload_from_db, "(self)", "testing"))


def obliterate_player(self):
    player_object = self.bot.players.get(self.player_steamid)
    if player_object.authenticated is True:
        player_object.switch_off("suicide")
        self.tn.kick(player_object, "You wanted it! Time to be born again!!")
        try:
            location_objects_dict = self.bot.locations.get(player_object.steamid)
            locations_to_remove = []
            for name, location_object in location_objects_dict.iteritems():
                locations_to_remove.append(location_object)
            for location_object in locations_to_remove:
                self.bot.locations.remove(player_object.steamid, location_object.identifier)
        except KeyError:
            pass
        self.bot.players.remove(player_object)
        self.bot.whitelist.remove(player_object)

    else:
        self.tn.send_message_to_player(player_object, "{} needs to enter the password to get access to sweet commands!".format(player_object.name), color='db500a')


actions_dev.append(("isequal", "obliterate me", obliterate_player, "(self)", "testing"))
