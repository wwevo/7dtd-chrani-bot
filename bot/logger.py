import logging
import logging.handlers

from bot.command_line_args import args_dict


class ExclusiveLevel(object):
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

    def add_logging_level(static, level_name, level_num, method_name=None):
        """ Example
        -------
        >>> add_logging_level('TRACE', logging.DEBUG - 5)
        >>> logging.getLogger(__name__).setLevel("TRACE")
        >>> logging.getLogger(__name__).trace('that worked')
        >>> logging.trace('so did this')
        >>> logging.TRACE
        5

        """
        if not method_name:
            method_name = level_name.lower()

        if hasattr(logging, level_name):
            raise AttributeError('{} already defined in logging module'.format(level_name))
        if hasattr(logging, method_name):
            raise AttributeError('{} already defined in logging module'.format(method_name))
        if hasattr(logging.getLoggerClass(), method_name):
            raise AttributeError('{} already defined in logger class'.format(method_name))

        # This method was inspired by the answers to Stack Overflow post
        # http://stackoverflow.com/q/2183233/2988730, especially
        # http://stackoverflow.com/a/13638084/2988730
        def log_for_level(self, message, *args, **kwargs):
            if self.isEnabledFor(level_num):
                self._log(level_num, message, args, **kwargs)

        def log_to_root(message, *args, **kwargs):
            logging.log(level_num, message, *args, **kwargs)

        logging.addLevelName(level_num, level_name)
        setattr(logging, level_name, level_num)
        setattr(logging.getLoggerClass(), method_name, log_for_level)
        setattr(logging, method_name, log_to_root)

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
        file_logger_info.addFilter(ExclusiveLevel(logging.INFO))  # makes this display only INFO-level messages
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
