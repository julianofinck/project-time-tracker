import logging
import os
import sys
from pathlib import Path


def set_logging_basic_config(
    entry_point_name: Path,
    level: str = "info",
):
    """
    Configures the logging settings for a Python script, typically used in the main entry point.

    Logs are written both to the console (stdout) and to a file located in a "logs" directory
    (or in the directory specified by the LOG_DIR environment variable). The log file is named
    after the entry point script with a `.log` extension.

    Parameters:
        entry_point_name (Path): The path to the main script (__file__).
        level (str): The desired log level as a string. Must be one of:
                     'debug', 'info', 'warning', 'error', 'critical'.

    Raises:
        NotImplementedError: If the provided log level is invalid.

    Example:
        set_logging_basic_config(__file__, 'debug')
    """
    level_lower = level.lower()
    if level_lower not in ("debug", "info", "warning", "error", "critical"):
        raise NotImplementedError(f"Log level is not valid: '{level}'")

    log_level = getattr(
        logging,
        level_upper := level_upper if (level_upper := level.upper()) else "INFO",
    )

    # Log config
    log_format = "%(asctime)s - [%(levelname)-8s] - %(name)s - %(message)s"
    log_datefmt = "%Y-%m-%dT%H:%M:%S"
    log_dir = Path(os.getenv("LOG_DIR", Path(entry_point_name).parent / "logs"))
    filename = log_dir / Path(Path(entry_point_name).stem).with_suffix(".log")
    filename.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        format=log_format,
        datefmt=log_datefmt,
        level=log_level,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(filename, mode="a", encoding="utf-8"),
        ],
        encoding="utf-8",
    )
