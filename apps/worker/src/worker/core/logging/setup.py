import logging


def configure_logging(log_level: str) -> None:
    """Configure basic worker logging.

    Args:
        log_level: Logging level name to apply.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )
