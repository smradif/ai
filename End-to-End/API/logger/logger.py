import os
import warnings
import traceback
from abc import ABC, abstractmethod


class LoggerInterface(ABC):
    """Interface for Logger"""

    @abstractmethod
    def info(self, source: str, message: str = ""):
        """Log useful info"""

    @abstractmethod
    def warning(self, source: str, message: str):
        """Log warrnings"""

    @abstractmethod
    def error(self, source: str, message: str):
        """Log errors"""


def get_logger():
    env = os.getenv("APP_ENV").lower()
    if env == "prod":
        return PRODLogger()
    if env == "uat":
        return UATLogger()
    return DEVLogger()


class DEVLogger(LoggerInterface):
    def info(self, source: str, message: str = ""):
        print(f"{source}: {message}" if message else source)

    def warning(self, source: str, message: str):
        warnings.warn(f"{source}: {message}")

    def error(self, source: str, message: str):
        traceback.print(f"{source}: {message}")


class UATLogger:
    def info(self, source: str, message: str = ""):
        print(f"{source}: {message}" if message else source)

    def warning(self, source: str, message: str):
        warnings.warn(f"{source}: {message}")

    def error(self, source: str, message: str):
        traceback.print(f"{source}: {message}")


class PRODLogger:
    def info(self, source: str, message: str = ""):
        print(f"{source}: {message}" if message else source)

    def warning(self, source: str, message: str):
        warnings.warn(f"{source}: {message}")

    def error(self, source: str, message: str):
        traceback.print(f"{source}: {message}")
