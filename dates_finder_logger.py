import logging


def init_logger(log_file_name='debug.log'):
    logger = logging.getLogger('dates_finder')
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(fmt='{asctime} [{levelname:^8s}] {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')

        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_file_name)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        logger.info('===================================== Logger initialized =====================================')
    return logger
