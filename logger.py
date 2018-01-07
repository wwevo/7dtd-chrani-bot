import logging
from command_line_args import args_dict


class Logger():
    def __init__(self):
        pass

    @staticmethod
    def get_logger(log_level):
        numeric_level = getattr(logging, log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)

        logger = logging.getLogger('chrani-bot')
        logger.setLevel(numeric_level)
        ch = logging.StreamHandler()
        ch.setLevel(numeric_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)10s @ %(threadName)s: %(message)s ')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger


logger = Logger().get_logger(args_dict["verbosity"].upper())
