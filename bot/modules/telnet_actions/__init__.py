def debuffplayer(self, player_object, buff):
    if not player_object.is_online:
        return False

    buff_list = [
        "bleeding",
        "foodPoisoning",
        "brokenLeg",
        "sprainedLeg"
    ]
    if buff not in buff_list:
        return False
    try:
        connection = self.tn
        command = "debuffplayer {player_steamid} {buff} {lbr}".format(player_steamid=player_object.steamid, buff=buff, lbr=b"\r\n")
        logger.info(command)
        connection.write(command)
    except Exception:
        return False

def buffplayer(self, player_object, buff):
    if not player_object.is_online:
        return False

    buff_list = [
        "firstAidLarge"
    ]
    if buff not in buff_list:
        return False
    try:
        connection = self.tn
        command = "buffplayer " + str(player_object.steamid) + " " + str(buff) + "\r\n"
        logger.info(command)
        connection.write(command)
    except Exception:
        return False

def set_admin_level(self, player_object, level):
    allowed_levels = [
        "2", "4"
    ]
    if level not in allowed_levels:
        return False
    try:
        connection = self.tn
        command = "admin add " + player_object.steamid + " " + str(level) + "\r\n"
        logger.info(command)
        connection.write(command)
    except Exception:
        return False


def remove_entity(self, entity_id):
    command = "removeentity " + str(entity_id) + b"\r\n"
    try:
        connection = self.tn
        connection.write(command)
        return True
    except Exception:
        return False

