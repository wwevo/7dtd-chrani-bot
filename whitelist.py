from player import Player


class Whitelist(object):
    whitelist_active = False
    players_dict = {
        '76561198040658370': {
            'name': 'ecv'
        },
        '76561198040548018': {
            'name': 'LadyAni'
        },
        '76561198010873208': {
            'name': 'ReflexTR'
        },
        '76561198003209403': {
            'name': 'hannesschmoschmannes'
        },
        '76561198237200194': {
            'name': 'NemoTheTerrible'
        }
    }

    def __init__(self):  # add at least myself *g*
        pass

    def add_player(self, player_object):
        try:
            is_in_dict = self.players_dict[player_object.steamid]
        except KeyError:
            self.players_dict.update({player_object.steamid: {'name': player_object.name}})

    def add_player_by_steamid(self, steamid):
        try:
            is_in_dict = self.players_dict[steamid]
        except KeyError:
            self.players_dict.update({steamid: {'name': 'generic'}})
        return True

    def remove_player(self, player_object):
        try:
            del self.players_dict[player_object.steamid]
        except KeyError:
            pass

    def remove_player_by_steamid(self, steamid):
        try:
            del self.players_dict[steamid]
            return True
        except KeyError:
            pass

    def player_is_allowed(self, player_object):
        try:
            is_in_dict = self.players_dict[player_object.steamid]
            return True
        except KeyError:
            return False

    def is_active(self):
        return self.whitelist_active

    def activate(self):
        self.whitelist_active = True

    def deactivate(self):
        self.whitelist_active = False
