import time


def timeout_occurred(timeout_in_seconds, timeout_start):
    if timeout_start == 0:  # set it to 0 to get a direct exit
        return True
    if timeout_in_seconds != 0:
        elapsed_time = time.time() - timeout_start
        if elapsed_time >= timeout_in_seconds:
            return True
    return None


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def is_alpha(word):
    try:
        return word.encode('ascii').isalpha()
    except Exception:
        return False
