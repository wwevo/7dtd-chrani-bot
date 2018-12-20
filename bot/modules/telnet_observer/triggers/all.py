import __main__
import common
import time
from bot.objects.player import Player


def entered_telnet(regex_results):
    chrani_bot = __main__.chrani_bot
    command = "entered_telnet"

    if not common.triggers_dict[command]["is_available"]:
        time.sleep(1)
        return

    command = regex_results.group("command")
    player_steamid = regex_results.group("player_steamid")
    player_name = regex_results.group("player_name")
    entity_id = ""
    try:
        entity_id = regex_results.group("entity_id")
    except Exception as e:
        print type(e)

    player_ip = ""
    try:
        player_ip = regex_results.group("player_ip")
    except Exception as e:
        print type(e)

    if command in ["connected", "Authenticating"]:
        player_found = False
        try:
            player_object = chrani_bot.players.get_by_steamid(player_steamid)
            player_found = True
        except KeyError:
            pass

        try:
            connecting_player = chrani_bot.player_observer.active_player_threads_dict[player_steamid]
        except KeyError:
            if not player_found:
                player_dict = {
                    "entityid": entity_id,
                    "name": player_name,
                    "steamid": player_steamid,
                    "ip": player_ip,
                    "is_logging_in": True,
                    "is_online": False,
                }

                player_object = Player(**player_dict)
                chrani_bot.players.upsert(player_object)

            chrani_bot.player_observer.start_player_thread(player_object)
            connecting_player = {
                "thread": chrani_bot.player_observer.active_player_threads_dict[player_steamid]["thread"],
                "player_object": player_object
            }

            connecting_player["thread"].trigger_action(connecting_player["player_object"], "entered the stream")


common.triggers_dict["entered_telnet"] = {
    "regex": [
        r"(?P<datetime>.+?) (?P<stardate>.+?) INF \[Steamworks.NET\]\s(?P<command>.*)\splayer:\s(?P<player_name>.*)\sSteamId:\s(?P<player_steamid>\d+)\s(.*)",
        r"(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<command>.*), entityid=(?P<entity_id>.*), name=(?P<player_name>.*), steamid=(?P<player_steamid>.*), steamOwner=(?P<owner_id>.*), ip=(?P<player_ip>.*)"
    ],
    "action": entered_telnet,
    "is_available": True
}


def entered_the_world(regex_results):
    chrani_bot = __main__.chrani_bot
    command = "entered_the_world"

    if not common.triggers_dict[command]["is_available"]:
        time.sleep(1)
        return

    player_steamid = regex_results.group("player_steamid")
    try:
        player_object = chrani_bot.players.get_by_steamid(player_steamid)
    except Exception as e:
        print(type(e))
        return

    command = regex_results.group("command")
    if command != "Teleport":
        player_object.pos_x = regex_results.group("pos_x")
        player_object.pos_y = regex_results.group("pos_y")
        player_object.pos_z = regex_results.group("pos_z")

        chrani_bot.player_observer.active_player_threads_dict[player_steamid]["thread"].trigger_action(player_object, "entered the world")


common.triggers_dict["entered_the_world"] = {
    "regex": [
        r"(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), position: (?P<pos_x>.*), (?P<pos_y>.*), (?P<pos_z>.*)\): EntityID=(?P<entity_id>.*), PlayerID='(?P<player_steamid>.*)', OwnerID='(?P<owner_steamid>.*)', PlayerName='(?P<player_name>.*)'",
    ],
    "action": entered_the_world,
    "is_available": True
}


def screamer_spawned(regex_results):
    chrani_bot = __main__.chrani_bot
    command = "screamer_spawned"

    if not common.triggers_dict[command]["is_available"]:
        time.sleep(1)
        return

    entity_id = regex_results.group("entity_id")
    pos_x = regex_results.group("pos_x")
    pos_y = regex_results.group("pos_y")
    pos_z = regex_results.group("pos_z")
    command = regex_results.group("command")
    zombie_name = regex_results.group("zombie_name")
    player_object = chrani_bot.players.get_by_steamid('system')
    if command == "Spawned" and zombie_name == "zombieScreamer":
        villages = chrani_bot.locations.find_by_type('village')
        for village in villages:
            if village.position_is_inside_boundary((pos_x, pos_y, pos_z)):
                chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "remove entity {}".format(entity_id))


common.triggers_dict["screamer_spawned"] = {
    "regex": [
        r"(?P<datetime>.+?) (?P<stardate>.+?) INF (?P<command>.+?) \[type=(.*), name=(?P<zombie_name>.+?), id=(?P<entity_id>.*)\] at \((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\) Day=(\d.*) TotalInWave=(\d.*) CurrentWave=(\d.*)",
    ],
    "action": screamer_spawned,
    "is_available": True
}


def airdrop_spawned(regex_results):
    chrani_bot = __main__.chrani_bot
    command = "airdrop_spawned"

    if not common.triggers_dict[command]["is_available"]:
        time.sleep(1)
        return

    pos_x = regex_results.group("pos_x")
    pos_y = regex_results.group("pos_y")
    pos_z = regex_results.group("pos_z")
    player_object = chrani_bot.players.get_by_steamid('system')
    chrani_bot.player_observer.actions.common.trigger_action(chrani_bot, player_object, player_object, "an airdrop has arrived @ ({pos_x} {pos_y} {pos_z})".format( pos_x=pos_x, pos_y=pos_y, pos_z=pos_z))


common.triggers_dict["airdrop_spawned"] = {
    "regex": [
        r"(?P<datetime>.+?)\s(?P<stardate>.+?)\sINF\sAIAirDrop:\sSpawned\ssupply\scrate\s@\s\(\((?P<pos_x>.*),\s(?P<pos_y>.*),\s(?P<pos_z>.*)\)\)",
    ],
    "action": airdrop_spawned,
    "is_available": True
}


def player_left_the_game(regex_results):
    chrani_bot = __main__.chrani_bot
    command = "player_left_the_game"

    if not common.triggers_dict[command]["is_available"]:
        time.sleep(1)
        return

    print("{} left the game after {} minutes".format(regex_results.group("player_name"), regex_results.group("time")))


common.triggers_dict["player_left_the_game"] = {
    "regex": [
        r"(?P<datetime>.+?) (?P<stardate>.+?) INF Player (?P<player_name>.*) (?P<command>.*) after (?P<time>.*) minutes",
    ],
    "action": player_left_the_game,
    "is_available": True
}


