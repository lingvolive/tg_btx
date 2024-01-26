import logging
from aiologger import Logger
from aiologger.handlers.files import AsyncTimedRotatingFileHandler
from aiologger.formatters.base import Formatter
import threading

from app.config.config import Config

DEFAULT_LOG_FMT = "%(asctime)s:[%(levelname)s]:%(name)s:(PID: %(process)d, TID: %(thread)d): %(message)s"
DEFAULT_LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S %z"

#Format of text log
#"%(ACTION),%(ACTIONS_PARAMS key1=val1,key2=val2 ),%ERR_DESC='%(ERROR_DESCRIPTION)'" 

class ThreadFormatter(Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        record.thread = threading.get_ident()
        return super().format(record)

def setup_logger(logger_name: str) -> Logger:
    config = Config()
    log_level = logging.getLevelName(config.log.log_level)
    log_fmt   = config.log.log_fmt
    log_date_fmt = config.log.log_date_fmt
    log_filename = config.log.log_file

    log_fmt =log_fmt or  DEFAULT_LOG_FMT 
    log_date_fmt = log_date_fmt or DEFAULT_LOG_DATE_FMT

    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger = Logger.with_default_handlers(
        name=logger_name, 
        level=log_level
    )

    file_handler = AsyncTimedRotatingFileHandler(
        filename=log_filename, 
        when=config.log.log_rotation_interval,
        interval=1, 
        utc=True,
        backup_count=7
    )
  
    file_handler.level = log_level
    file_handler.formatter = ThreadFormatter(log_fmt, log_date_fmt)
    
    logger.add_handler(file_handler)

    return logger
