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

    # Add new handlers with formatter
    formatter = logging.Formatter(log_format)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Also configure component loggers
    component_loggers = [
        "memory",
        "driver",
        "communication",
        "process",
        "resource",
        "ai",
        "services",
    ]
    for component in component_loggers:
        component_logger = logging.getLogger(component)
        component_logger.setLevel(level)
        component_logger.handlers.clear()
        for handler in handlers:
            component_logger.addHandler(handler)
