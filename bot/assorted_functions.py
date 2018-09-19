import time
import math


def timeout_occurred(timeout_in_seconds, timeout_start):
    if timeout_start == 0:  # set it to 0 to get a direct exit
        return True
    if timeout_start is None:
        return None
    if timeout_in_seconds != 0:
        elapsed_time = time.time() - timeout_start
        if elapsed_time >= timeout_in_seconds:
            return True
    return None


def timepassed_occurred(timeout_in_seconds, threshold):
    if threshold == 0:
        return True
    if threshold is None:
        return None
    if timeout_in_seconds != 0:
        if threshold >= timeout_in_seconds:
            return True
    return None


def byteify(input_to_byteify):
    if isinstance(input_to_byteify, dict):
        return {byteify(key): byteify(value) for key, value in input_to_byteify.iteritems()}
    elif isinstance(input_to_byteify, list):
        return [byteify(element) for element in input_to_byteify]
    elif isinstance(input_to_byteify, unicode):
        return input_to_byteify.encode('utf-8')
    else:
        return input_to_byteify


def is_alpha(word):
    try:
        return word.encode('ascii').isalpha()
    except Exception:
        return False


def round_to_region_grid(number):
    return int(math.floor(number / 512))


def get_region_grid(pos_x, pos_z):
    grid_x = round_to_region_grid(pos_x)
    grid_z = round_to_region_grid(pos_z)

    return grid_x, grid_z


def get_region_string(pos_x, pos_z):
    grid_x, grid_z = get_region_grid(pos_x, pos_z)

    try:
        region_string = str(grid_x) + "." + str(grid_z) + ".7rg"
    except TypeError:
        raise TypeError

    return region_string


class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d


class ResponseMessage(object):
    messages = dict

    def __init__(self):
        self.messages = {}

    def add_message(self, message, result=True):
        self.messages.update({message: result})

    def get_message_dict(self):
        return self.messages

