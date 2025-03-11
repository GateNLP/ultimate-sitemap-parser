import logging
from typing import Dict, Optional


def format_help(choices: Dict[str, str], opt_help: str) -> str:
    """Generate help text for argparse choices.

    :param choices: Dictionary of choices {choice: help}
    :param opt_help: Help text for the option:
    :return: Help text for argparse choices.
    """
    h = f"{opt_help} (default: %(default)s)\nchoices:\n"

    for fmt, key in choices.items():
        h += f"  {fmt}: {key}\n"

    return h


def tabs(n: int):
    """Generate n tabs."""
    return "\t" * n


_log_levels = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def setup_logging(verbosity: int, log_path: Optional[str]) -> None:
    log_level = _log_levels.get(verbosity, logging.DEBUG)
    if log_path is not None:
        logging.basicConfig(level=log_level, filename=log_path)
    else:
        logging.basicConfig(level=log_level)
