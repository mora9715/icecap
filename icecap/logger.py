import logging
from typing import Optional, List


def configure_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    handlers: Optional[List[logging.Handler]] = None,
) -> None:
    """
    Configure logging for the IceCap library.

    By default, logs to stdout at INFO level with plain text format.

    Args:
        level: Logging level (default: logging.INFO)
        log_format: Log message format string (default: simple format)
        handlers: List of logging handlers (default: [StreamHandler()])
    """
    if log_format is None:
        log_format = "[%(levelname)s] %(name)s: %(message)s"

    if handlers is None:
        handlers = [logging.StreamHandler()]

    logger = logging.getLogger("icecap")
    logger.setLevel(level)

    logger.handlers.clear()

    formatter = logging.Formatter(log_format)

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
