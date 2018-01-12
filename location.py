import math


class Location(object):
    owner = str
    name = str
    pos_x = float
    pos_y = float
    pos_z = float
    shape = str
    radius = float
    # Todo: region should be a list as a location nd it's effect can spawn several regions. capture all regions if empty
    region = str

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def update(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def player_is_outside_boundary(self, player_object):
        if self.shape == "sphere":
            distance_to_lobby_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                    float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                    float(self.pos_z) - float(player_object.pos_z)) ** 2))

        if distance_to_lobby_center > self.radius:
            return True
        else:
            return False

    def player_is_near_boundary_inside(self, player_object):
        if self.shape == "sphere":
            distance_to_lobby_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2))

        if distance_to_lobby_center >= (self.radius * 0.5) and distance_to_lobby_center <= self.radius:
            return True
        else:
            return False

    def player_is_near_boundary_outside(self, player_object):
        if self.shape == "sphere":
            distance_to_lobby_center = float(math.sqrt(
                (float(self.pos_x) - float(player_object.pos_x)) ** 2 + (
                        float(self.pos_y) - float(player_object.pos_y)) ** 2 + (
                        float(self.pos_z) - float(player_object.pos_z)) ** 2))

        if distance_to_lobby_center >= self.radius and distance_to_lobby_center <= (self.radius * 1.5):
            return True
        else:
            return False

