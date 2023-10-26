import logging
from config import LOGGING_LEVEL

HINFO_LEVEL_NUM = 25
HDEBUG_LEVEL_NUM = 23


def initialize_logger(logging_level):
    """
    Python custom logging initialization
    """
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-4s | %(message)s",
        level=logging_level,
        datefmt="%H:%M:%S",
    )


class CustomLogger(logging.Logger):
    """
    Custom logger
    """

    def hinfo(self, msg, *args, **kwargs):
        pass

    def hdebug(self, msg, *args, **kwargs):
        pass


def getLogger(name: str) -> CustomLogger:
    logging.addLevelName(HINFO_LEVEL_NUM, "HINFO")
    logging.addLevelName(HDEBUG_LEVEL_NUM, "HDEBUG")

    logger = logging.getLogger(name)

    def hinfo(message, *args, **kws):
        if logger.isEnabledFor(HINFO_LEVEL_NUM):
            # Yes, logger takes its '*args' as 'args'.
            logger._log(
                HINFO_LEVEL_NUM, message, args, **kws
            )  # pylint: disable=W0212

    def hdebug(message, *args, **kws):
        if logger.isEnabledFor(HDEBUG_LEVEL_NUM):
            # Yes, logger takes its '*args' as 'args'.
            logger._log(
                HDEBUG_LEVEL_NUM, message, args, **kws
            )  # pylint: disable=W0212

    logger.hinfo = hinfo  # type: ignore
    logger.hdebug = hdebug  # type: ignore
    return logger  # type: ignore

_logging_level = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "HINFO": HINFO_LEVEL_NUM,
    "HDEBUG": HDEBUG_LEVEL_NUM,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARN,
}.get(LOGGING_LEVEL, HINFO_LEVEL_NUM)

initialize_logger(_logging_level)
