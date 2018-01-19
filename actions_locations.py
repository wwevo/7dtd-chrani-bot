import math
import re
from location import Location

actions_locations = []


def create_location(self, player_object, locations, command):
    if player_object.authenticated:
        regexp = r"add (?:location\s(?<name>.+?))\s(?:owner\s(?<owner>.+?))\s(?:shape\s(?<shape>.+?))\s(?:radius\s(?<radius>\d{1,3}))\s(?:boundary\s(?<boundary>\d{1,3}))\s(?:description\s\"(?<description>.+?)\")\s(?:pos\s(?<pos_x>-?\d{1,5})\s?,\s?(?<pos_y>-?\d{1,5})\s?,\s?(?<pos_z>-?\d{1,5}))\s(?:dim\s(?<width>\d{1,5})\s?,\s?(?<height>\d{1,5})\s?,\s?(?<length>\d{1,5}))"
        p = re.search(regexp, command)
        if p:
            name = p.group('name')
            owner = p.group('owner')
            shape = p.group('shape')
            radius = p.group('radius')
            description = p.group('description')
            pos_x = p.group('pos_x')
            pos_y = p.group('pos_y')
            pos_z = p.group('pos_z')
            width = p.group('width')
            height = p.group('height')
            length = p.group('length')
            boundary = p.group('boundary')

            location_dict = dict(
                name=name,
                owner=owner,
                description=description,
                pos_x=int(pos_x),
                pos_y=int(pos_y),
                pos_z=int(pos_z),
                width=int(width),
                height=int(height),
                length=int(length),
                shape=shape,
                radius=radius,
                boundary_percentage=boundary,
                region=[]
            )
    else:
        self.tn.send_message_to_player(player_object, "{} is no authorized no nope. should go read read!".format(player_object.name))


actions_locations.append(("startswith", "add location", create_location, "(self, player_object, locations, command)"))
