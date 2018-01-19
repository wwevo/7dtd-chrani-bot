from command_line_args import args_dict
import json
import os
from location import Location


class Locations(object):
    """ made this to hold all system relevant functions regarding locations

    used to store persistent data, for now in a pickled shelve, but we can easily use any db here.
    at no other point in the project should read or write functions be performed!

    files will be named <steamid>.shelve,
    except for system locations like the lobby, they will be shelved in system.shelve
    """

    root = 'data/locations/'
    prefix = args_dict['Database-file']

    locations_dict = {}

    def __init__(self):
        self.load_all()

    def load_all(self):
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file.startswith(self.prefix) and file.endswith('.json'):
                    with open(self.root + file) as file_to_read:
                        location_dict = json.load(file_to_read)
                        try:
                            self.locations_dict[str(location_dict['owner'])].update({str(location_dict['name']): Location(**location_dict)})
                        except KeyError:
                            self.locations_dict[str(location_dict['owner'])] = {str(location_dict['name']): Location(**location_dict)}

    def add(self, location, save=False):
        try:
            self.locations_dict[location.owner].update({location.name: location})
        except KeyError:
            self.locations_dict[location.owner] = {location.name: location}
        if save:
            self.save(location)

    def get(self, location_owner, location_name):
        try:
            location = self.locations_dict[location_owner][location_name]
            return location
        except KeyError:
            raise

    def remove(self):
        pass

    def save(self, location):
        dict_to_save = location.__dict__
        with open(self.root + self.prefix + '_' + location.owner + '_' + location.name + '.json', 'w+') as file_to_write:
            json.dump(dict_to_save, file_to_write)
