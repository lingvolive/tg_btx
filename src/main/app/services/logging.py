
import logging
from logging.handlers import TimedRotatingFileHandler

from app.config.config import Config

def setup_logger(logger_name:str, config: Config = None):

    if(config is None):
        config = Config()

    log_level = logging.getLevelName(config.log.log_level)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    formatter = logging.Formatter(config.log.log_fmt, config.log.log_date_fmt)

    file_handler = TimedRotatingFileHandler(config.log.log_file, when='midnight', backupCount=7)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger