"""
Creates a logger that propagates to root.
This way, I can create a log per specific module

✅, ❌, ⚙️
"""

import datetime
import logging
import os
import sys


def create_logger(
    logger_name: str = "main", level=logging.DEBUG, log_file=None, cleanroot=False
) -> logging.Logger:
    """Creates a logger with FileHandler and StreamHandler

    DEBUG	  10  Detailed information, typically of interest only when diagnosing problems.
    INFO	  20  Confirmation that things are working as expected.
    WARNING	  30  An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
    ERROR	  40  Due to a more serious problem, the software has not been able to perform some function.
    CRITICAL  50  A serious error, indicating that the program itself may be unable to continue running.
    """
    # Get root logger
    root = logging.getLogger()

    # Clean any handler added by other parties
    if cleanroot:
        root.handlers.clear()

    # Create logger
    logger = root.getChild(logger_name)

    # Set format, level and whether it propagates to the root logger
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    logger.setLevel(level)
    logger.propagate = True

    # Add StreamHandler (print log messages in console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add FileHandler
    if log_file:
        log_dir = "logs/"
        os.makedirs(log_dir, exist_ok=True)

        # Module-specific
        if os.path.splitext(log_file)[-1] != ".log":
            log_file += ".log"

        # Clean 3 months or older logger
        logfile_path = f"{log_dir}{log_file}"
        if os.path.exists(logfile_path):
            _clear_logger(logfile_path, months=3)

        file_handler = logging.FileHandler(logfile_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Declare creation
    logger.debug(f"Created log '{logger.name}'!")

    return logger


def fetch_all_loggers() -> dict:
    return {
        name: logger
        for name, logger in logging.Logger.manager.loggerDict.items()
        if isinstance(logger, logging.Logger)
    }


def _is_new_entry(entry, cutoff_date):
    try:
        timestamp_str = entry.split(" ")[0] + " " + entry.split(" ")[1]
        entry_date = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
        return entry_date > cutoff_date
    except (IndexError, ValueError):
        return False


def _clear_logger(logfile_path, months):
    # Calculate the cutoff date (3 months ago)
    days = 30 * months
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

    # Read the log file, filter old entries, and write back to the file
    with open(logfile_path, "r") as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if _is_new_entry(line, cutoff_date)]

    with open(logfile_path, "w") as file:
        file.writelines(filtered_lines)
