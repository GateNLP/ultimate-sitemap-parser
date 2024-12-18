"""Logging utilities."""

import logging


class Logger:
    """
    Logging helper class.
    """

    __LEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    """Valid logging levels and their "logging" counterparts."""

    __DEFAULT_LEVEL = "INFO"
    """Default logging level."""

    __slots__ = [
        # "logging" object
        "__l",
    ]

    def __init__(self, name: str):
        """
        Initialize logger object for a given name.

        :param name: Module name that the logger should be initialized for.
        """

        self.__l = logging.getLogger(name)

    def error(self, message: str) -> None:
        """
        Log error message.

        :param message: Message to log.
        """
        self.__l.error(message)

    def warning(self, message: str) -> None:
        """
        Log warning message.

        :param message: Message to log.
        """
        self.__l.warning(message)

    def info(self, message: str) -> None:
        """
        Log informational message.

        :param message: Message to log.
        """
        self.__l.info(message)

    def debug(self, message: str) -> None:
        """
        Log debugging message.

        :param message: Message to log.
        """
        self.__l.debug(message)


def create_logger(name: str) -> Logger:
    """
    Create and return Logger object.

    :param name: Module name that the logger should be initialized for.
    :return: Logger object.
    """
    return Logger(name=name)
