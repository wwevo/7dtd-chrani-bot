from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
import json
import os
import math
from bot.modules.logger import logger
from bot.objects.location import Location
import pathlib2


class Locations(object):

    chrani_bot = object

    root = str
    extension = str

    all_locations_dict = dict
    locations_dict = dict

    def __init__(self, chrani_bot):
        self.chrani_bot = chrani_bot
        self.root = "data/{db}/locations".format(db=args_dict['Database-file'])
        self.extension = "json"

        self.load_all()

    def load_all(self):
        locations_dict = {}
        for root, dirs, files in os.walk(self.root):
            files_to_remove_list = []
            for filename in files:
                if filename.endswith(".{ext}".format(ext=self.extension)):
                    with open("{root}/{filename}".format(root=self.root, filename=filename)) as file_to_read:
                        try:
                            location_dict = byteify(json.load(file_to_read))
                        except ValueError:
                            files_to_remove_list.append("{root}/{filename}".format(root=self.root, filename=filename))
                            continue

                        try:
                            locations_dict[str(location_dict['owner'])].update({str(location_dict['identifier']): Location(**location_dict)})
                        except KeyError:
                            locations_dict[str(location_dict['owner'])] = {str(location_dict['identifier']): Location(**location_dict)}

            for file_to_remove in files_to_remove_list:
                try:
                    os.remove(file_to_remove)
                    logger.debug("removed invalid location file: {}".format(file_to_remove))
                except OSError, e:
                    logger.exception(e)

        self.locations_dict = locations_dict
        self.all_locations_dict = locations_dict
        return locations_dict

    def upsert(self, location_object, save=False):
        try:
            self.locations_dict[location_object.owner].update({location_object.identifier: location_object})
        except KeyError:
            self.locations_dict[location_object.owner] = {location_object.identifier: location_object}
        if save:
            self.save(location_object)

    def get(self, location_owner=None, location_identifier=None):
        if location_identifier is None:
            try:
                locations_dict = self.locations_dict[location_owner]
                return locations_dict
            except KeyError:
                return {}
        else:
            try:
                location_object = self.locations_dict[location_owner][location_identifier]
                return location_object
            except KeyError:
                raise

    def find_by_distance(self, start_coords, distance_in_blocks, location_identifier=None):
        location_in_reach_list = []
        locations_dict = self.locations_dict
        for player_steamid, locations in locations_dict.iteritems():
            for identifier, location in locations.iteritems():
                if location_identifier is not None and identifier != location_identifier:
                    continue

                distance = math.sqrt((float(location.pos_x) - float(start_coords[0]))**2 + (float(location.pos_y) - float(start_coords[1]))**2 + (float(location.pos_z) - float(start_coords[2]))**2)
                if distance < distance_in_blocks:
                    location_in_reach_list.append(location)

        return location_in_reach_list

    def find_by_type(self, location_type=None):
        locations_found = []
        locations_dict = self.locations_dict
        for player_steamid, locations in locations_dict.iteritems():
            for identifier, location in locations.iteritems():
                if location_type is not None and location.type != location_type:
                    continue

                locations_found.append(location)

        return locations_found

    def get_available_locations(self, player_object):
        available_locations_dict = {}
        locations_dict = self.locations_dict
        for player_steamid, locations in locations_dict.iteritems():
            for identifier, location_object in locations.iteritems():
                if location_object.enabled is True and (location_object.is_public is True or player_steamid == player_object.steamid):
                    try:
                        available_locations_dict.update({location_object.identifier: location_object})
                    except KeyError:
                        available_locations_dict = {location_object.identifier: location_object}

        return available_locations_dict

    def remove(self, location_owner, location_identifier):
        try:
            location_object = self.locations_dict[location_owner][location_identifier]
            filename = "{root}/{object_owner}_{object_identifier}.{ext}".format(root=self.root, object_owner=location_object.owner, object_identifier=location_object.identifier, ext=self.extension)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    del self.locations_dict[location_owner][location_identifier]
                    return True
                except OSError, e:
                    logger.exception(e)

            return False
        except KeyError:
            raise

    def save(self, location_object):
        dict_to_save = {
            "messages_dict": location_object.messages_dict,
            "show_messages": location_object.show_messages,
            "show_warning_messages": location_object.show_messages,
            "radius": location_object.radius,
            "is_public": location_object.is_public,
            "warning_boundary": location_object.warning_boundary,
            "width": location_object.width,
            "length": location_object.length,
            "height": location_object.height,
            "enabled": location_object.enabled,
            "protected_core": location_object.protected_core,
            "protected_core_whitelist": location_object.protected_core_whitelist,
            "identifier": location_object.identifier,
            "owner": location_object.owner,
            "name": location_object.name,
            "description": location_object.description,
            "pos_x": location_object.pos_x,
            "pos_y": location_object.pos_y,
            "pos_z": location_object.pos_z,
            "tele_x": location_object.tele_x,
            "tele_y": location_object.tele_y,
            "tele_z": location_object.tele_z,
            "shape": location_object.shape,
            "region_list": location_object.region_list,
            "teleport_target": location_object.teleport_target,
            "teleport_active": location_object.teleport_active,
            "list_of_players_inside": location_object.list_of_players_inside,
            "list_of_players_inside_core": location_object.list_of_players_inside_core,
            "type": location_object.type
        }

        try:
            pathlib2.Path(self.root).mkdir(parents=True, exist_ok=True)
            with open("{root}/{object_owner}_{object_identifier}.{ext}".format(root=self.root, object_owner=location_object.owner, object_identifier=location_object.identifier, ext=self.extension), 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Saved location-record {object_identifier} for player {object_owner}.".format(object_identifier=location_object.identifier, object_owner=location_object.owner))
        except Exception as e:
            logger.exception("Saving location-record {object_identifier} for player {object_owner} failed: {status}.".format(object_identifier=location_object.identifier, object_owner=location_object.owner, status=e.message))
            return False

        return True
