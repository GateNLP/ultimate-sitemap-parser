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


def setup_logging(log_level: int, log_path: Optional[str]) -> None:
    if log_path is not None:
        logging.basicConfig(level=log_level, filename=log_path)
    else:
        logging.basicConfig(level=log_level)
