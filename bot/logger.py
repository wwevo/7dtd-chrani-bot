import logging
import logging.handlers

from bot.command_line_args import args_dict


class Logger:
    root = str
    prefix = str

    def __init__(self):
        self.root = 'data/logs/'
        self.prefix = args_dict["verbosity"].upper()

    def get_logger(self, log_level):
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

        handler = logging.handlers.RotatingFileHandler(self.root + self.prefix)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger


logger = Logger().get_logger(args_dict["verbosity"].upper())
