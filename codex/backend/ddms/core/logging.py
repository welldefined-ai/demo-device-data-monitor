import logging
from typing import Literal

_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | str = "INFO",
) -> None:
    """Configure application-wide logging.

    This function is idempotent: if logging is already configured it will only
    adjust the root level, otherwise it installs a basic configuration.
    """
    normalized_level = str(level).upper()
    log_level = getattr(logging, normalized_level, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(log_level)
        return

    logging.basicConfig(level=log_level, format=_FORMAT)
