from bot.command_line_args import args_dict
from bot.assorted_functions import byteify
import json
import os
from bot.logger import logger
from bot.location import Location


class Locations(object):
    """ made this to hold all system relevant functions regarding locations

    used to store persistent data, for now in a pickled shelve, but we can easily use any db here.
    at no other point in the project should read or write functions be performed!

    files will be named <steamid>.shelve,
    except for system locations like the lobby, they will be shelved in system.shelve
    """

    root = str
    prefix = str

    locations_dict = dict

    def __init__(self):
        self.root = 'data/locations/'
        self.prefix = args_dict['Database-file']
        self.locations_dict = {}

    def load_all(self):
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.startswith(self.prefix) and filename.endswith('.json'):
                    with open(self.root + filename) as file_to_read:
                        location_dict = byteify(json.load(file_to_read))
                        try:
                            self.locations_dict[str(location_dict['owner'])].update({str(location_dict['identifier']): Location(**location_dict)})
                        except KeyError:
                            self.locations_dict[str(location_dict['owner'])] = {str(location_dict['identifier']): Location(**location_dict)}

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
            filename = self.root + self.prefix + '_' + location_object.owner + '_' + location_object.identifier + '.json'
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    del self.locations_dict[location_owner][location_identifier]
                except OSError, e:
                    logger.error("Error: {} - {}.".format(e.filename, e.strerror))
            else:
                print("Sorry, I can not find {} file.".format(filename))
            pass
        except KeyError:
            raise

    def save(self, location_object):
        dict_to_save = location_object.__dict__
        with open(self.root + self.prefix + '_' + location_object.owner + '_' + location_object.identifier + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write, indent=4)
