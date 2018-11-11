from bot.assorted_functions import byteify
import json
from bot.modules.logger import logger

from bot.command_line_args import args_dict


class Settings(object):

    root = str
    prefix = str
    extension = str

    settings_dict = dict

    def __init__(self):
        self.root = 'data/configurations'
        self.prefix = args_dict['Database-file']
        self.extension = "json"

        self.load_all()

    def load_all(self):
        filename = "{}/{}.{}".format(self.root, self.prefix, self.extension)
        try:
            with open(filename) as file_to_read:
                self.settings_dict = byteify(json.load(file_to_read))
        except IOError:  # no settings file available
            pass

    def get_setting_by_name(self, *args, **kwargs):
        setting_name = kwargs.get('name', None)
        default_value = kwargs.get('default', None)
        try:
            setting_value = self.settings_dict[setting_name]
        except (TypeError, KeyError):
            logger.debug("could not find '{setting_name}' in the settings file, using default values.".format(setting_name=setting_name))
            setting_value = default_value

        return setting_value

    def save(self, available_settings_dict):
        dict_to_save = available_settings_dict
        filename = '{}/{}.{}'.format(self.root, self.prefix, self.extension)
        try:
            with open(filename, 'w+') as file_to_write:
                json.dump(dict_to_save, file_to_write, indent=4, sort_keys=True)
            logger.debug("Updated settings file.")
        except:
            logger.exception("Updating settings file failed.")
