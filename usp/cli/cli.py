from argparse import ArgumentParser

from usp.cli import _ls as ls_cmd
from usp import __version__


def main():
    parser = ArgumentParser(prog="usp", description="Ultimate Sitemap Parser")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s v{__version__}"
    )

    subparsers = parser.add_subparsers(required=False, title="commands", metavar="")
    ls_cmd.register(subparsers)

    args = parser.parse_args()

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()

    exit(0)


if __name__ == "__main__":
    main()
