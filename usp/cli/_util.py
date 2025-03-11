import logging
from argparse import Action
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


class CountAction(Action):
    """Modified version of argparse._CountAction to output better help."""

    def __init__(
        self,
        option_strings,
        dest,
        default=None,
        required=False,
        help=None,
        max_count=None,
    ):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help,
        )
        self.max_count = max_count

    def __call__(self, parser, namespace, values, option_string=None):
        count = getattr(namespace, self.dest, None)
        if count is None:
            count = 0
        if self.max_count:
            count = min(count, self.max_count)
        setattr(namespace, self.dest, count + 1)

    def format_usage(self):
        option_str = self.option_strings[0]
        if self.max_count is None:
            return option_str
        letter = self.option_strings[0][1]
        usages = [f"-{letter * i}" for i in range(1, self.max_count + 1)]
        return "/".join(usages)


def setup_logging(verbosity: int, log_path: Optional[str]) -> None:
    log_level = _log_levels.get(verbosity, logging.DEBUG)
    if log_path is not None:
        logging.basicConfig(level=log_level, filename=log_path)
    else:
        logging.basicConfig(level=log_level)
