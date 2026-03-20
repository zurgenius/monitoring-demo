import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


from pythonjsonlogger import json


LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

CONSOLE_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
CONSOLE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
JSONL_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(funcName)s %(pathname)s %(lineno)d %(message)s"


class MaxLevelFilter(logging.Filter):
    """A logging filter to allow log messages up to a defined maximum level.

    This class extends the logging.Filter class, providing functionality
    to filter log records so that only messages with a severity level less
    than or equal to the specified maximum level are passed through.
    """

    def __init__(self, max_level: int) -> None:
        """Initializes an instance of the class.

        Args:
            max_level:
                The maximum level parameter used to configure the instance.
        """
        self.max_level = max_level
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


def _configure_stdout(level: str) -> logging.StreamHandler:
    """Configure a stdout stream handler for logging.

    Creates a handler that outputs log messages up to INFO level to stdout,
    with request ID filtering and console formatting.

    Args:
        level:
            The minimum logging level as a string (e.g., 'DEBUG', 'INFO').

    Returns:
        A configured StreamHandler instance writing to stdout.
    """
    fmt = logging.Formatter(CONSOLE_LOG_FORMAT, datefmt=CONSOLE_DATE_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(MaxLevelFilter(logging.INFO))
    handler.setFormatter(fmt)
    return handler


def _configure_stderr() -> logging.StreamHandler:
    """Configure a stderr stream handler for logging.

    Creates a handler that outputs log messages at WARNING level and above
    to stderr, with `request` ID filtering and console formatting.

    Returns:
        A configured StreamHandler instance writing to stderr.
    """
    fmt = logging.Formatter(CONSOLE_LOG_FORMAT, datefmt=CONSOLE_DATE_FORMAT)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(fmt)
    return handler


def _configure_jsonl() -> TimedRotatingFileHandler:
    """Configure a JSON Lines file handler with time-based rotation.

    Creates a handler that writes log records as JSON objects to a rotating
    file, with configurable rotation schedule and backup retention.

    Args:
        config:
            A LazySettings object containing JSONL handler configuration with
            attributes:
            - directory: Path to the log directory.
            - when: Time unit for rotation (e.g., 'midnight', 'H').
            - interval: Number of time units between rotations (default: 1).
            - backup_count: Number of backup files to keep (default: 0).
            - level: The minimum logging level for this handler.

    Returns:
        A configured TimedRotatingFileHandler instance.
    """
    filename = Path("/app") / "log.jsonl"

    fmt = json.JsonFormatter(
        JSONL_LOG_FORMAT,
        rename_fields={
            "levelname": "level",
            "name": "logger",
            "pathname": "file",
            "lineno": "line",
            "funcName": "function",
        },
        timestamp=True,
    )

    handler = TimedRotatingFileHandler(
        filename=filename,
        when="D",
        interval=1,
        backupCount=0,
        utc=True,
    )
    handler.setLevel("DEBUG")
    handler.setFormatter(fmt)
    return handler


def _configure_uvicorn() -> None:
    """Configure Uvicorn loggers to propagate to the root logger.

    Clears existing handlers from Uvicorn-related loggers and enables
    propagation so they use the application's logging configuration.
    """
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True


def configure_logging() -> None:
    """Configure the application's logging system.

    Sets up the root logger with stdout, stderr, and optionally JSONL handlers.
    Also configures Uvicorn loggers to use the application's logging setup.

    Args:
        config:
            A LazySettings object containing logging configuration with:
            - level: The root logging level as a string.
            - jsonl.enabled: Whether to enable JSONL file logging.
            - jsonl: JSONL handler configuration (if enabled).

    Raises:
        ValueError:
            If the specified logging level is not valid.
    """
    level = "DEBUG"

    if level not in LOG_LEVELS:
        raise ValueError(
            f"Invalid logging level: {level}, must be one of {logging._nameToLevel.keys()}"
        )

    root = logging.getLogger()
    root.setLevel(level)

    root.handlers.clear()

    root.addHandler(_configure_stdout(level))
    root.addHandler(_configure_stderr())
    root.addHandler(_configure_jsonl())

    _configure_uvicorn()


__all__ = ("configure_logging",)
