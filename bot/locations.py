from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
import json
import os
from bot.logger import logger
from bot.location import Location


class Locations(object):

    root = str
    prefix = str
    extension = str

    locations_dict = dict

    def __init__(self):
        self.root = 'data/locations'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.locations_dict = {}

    def load_all(self, store=False):
        locations_dict = {}
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith(".{}".format(self.extension)):
                    with open("{}/{}".format(self.root, filename)) as file_to_read:
                        location_dict = byteify(json.load(file_to_read))
                        try:
                            locations_dict[str(location_dict['owner'])].update({str(location_dict['identifier']): Location(**location_dict)})
                        except KeyError:
                            locations_dict[str(location_dict['owner'])] = {str(location_dict['identifier']): Location(**location_dict)}
            if store is True:
                self.locations_dict = locations_dict
            return locations_dict

    def upsert(self, location_object, save=False):
        try:
            self.locations_dict[location_object.owner].update({location_object.identifier: location_object})
        except KeyError:
            self.locations_dict[location_object.owner] = {location_object.identifier: location_object}
        if save:
            self.save(location_object)

    def get(self, location_owner, location_identifier=None):
        if location_identifier is None:
            try:
                locations_dict = self.locations_dict[location_owner]
                return locations_dict
            except KeyError:
                raise
        else:
            try:
                location_object = self.locations_dict[location_owner][location_identifier]
                return location_object
            except KeyError:
                raise

    def remove(self, location_owner, location_identifier):
        try:
            location_object = self.locations_dict[location_owner][location_identifier]
            filename = "{}/{}_{}_{}.{}".format(self.root, self.prefix, location_object.owner, location_object.identifier, self.extension)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    del self.locations_dict[location_owner][location_identifier]
                except OSError, e:
                    logger.error("Error: {} - {}.".format(e.filename, e.strerror))
            else:
                logger.error("Sorry, I can not find {} file.".format(filename))
            pass
        except KeyError:
            raise

    def save(self, location_object):
        dict_to_save = location_object.__dict__
        with open("{}/{}_{}_{}.{}".format(self.root, self.prefix, location_object.owner, location_object.identifier, self.extension), 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
