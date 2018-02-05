import logging
import logging.handlers

from bot.command_line_args import args_dict


class exclusiveLevel(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno == self.__level


class Logger:
    root = str
    prefix = str
    extension = str

    def __init__(self):
        self.root = 'data/logs'
        self.extension = "log"

    def get_logger(self, log_level):
        numeric_level = getattr(logging, log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)

        logger_object = logging.getLogger('chrani-bot')
        logger_object.setLevel(numeric_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)10s @ %(threadName)s: %(message)s ')

        console_logger = logging.StreamHandler()
        console_logger.setFormatter(formatter)
        logger_object.addHandler(console_logger)

        log_level = "INFO"
        filename_info = "{}/{}.{}".format(self.root, log_level.lower(), self.extension)
        file_logger_info = logging.handlers.TimedRotatingFileHandler(filename_info, when='midnight', interval=1, backupCount=28)
        file_logger_info.setLevel(logging.DEBUG)
        file_logger_info.addFilter(exclusiveLevel(logging.INFO))
        file_logger_info.setFormatter(formatter)
        logger_object.addHandler(file_logger_info)

        log_level = "DEBUG"
        filename_debug = "{}/{}.{}".format(self.root, log_level.lower(), self.extension)
        file_logger_debug = logging.handlers.TimedRotatingFileHandler(filename_debug, when='midnight', interval=1, backupCount=28)
        file_logger_debug.setLevel(logging.DEBUG)
        file_logger_debug.setFormatter(formatter)
        logger_object.addHandler(file_logger_debug)

        return logger_object


logger = Logger().get_logger(args_dict["verbosity"].upper())
