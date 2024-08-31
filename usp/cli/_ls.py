import argparse
import sys
from typing import Iterator

from usp.cli._util import tabs, format_help
from usp.objects.sitemap import AbstractSitemap
from usp.tree import sitemap_tree_for_homepage

LS_FORMATS = {
    "tabtree": "Sitemaps and pages, nested with tab indentation",
    "pages": "Flat list of pages, one per line",
}


def register(subparsers):
    ls_parser = subparsers.add_parser(
        "ls",
        help="List sitemap pages",
        description="download, parse and list the sitemap structure",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ls_parser.add_argument("url", type=str, help="URL of the site including protocol")
    ls_parser.add_argument(
        "-f",
        "--format",
        choices=LS_FORMATS,
        default="tabtree",
        help=format_help(LS_FORMATS, "set output format"),
        metavar="",
    )
    ls_parser.add_argument(
        "-r",
        "--no-robots",
        action="store_true",
        help="don't discover sitemaps through robots.txt",
    )
    ls_parser.add_argument(
        "-k",
        "--no-known",
        action="store_true",
        help="don't discover sitemaps through well-known URLs",
    )
    ls_parser.add_argument(
        "-u",
        "--strip-url",
        action="store_true",
        help="strip the supplied URL from each page and sitemap URL",
    )
    ls_parser.set_defaults(no_robots=False, no_known=False, strip_url=False)

    ls_parser.set_defaults(func=ls)


def _strip_url(url: str, prefix: str):
    url = url.removeprefix(prefix)

    if not url.startswith("/") and prefix != "":
        return "/" + url
    return url


def _list_page_urls(sitemap: AbstractSitemap, prefix: str = "") -> Iterator[str]:
    for page in sitemap.all_pages():
        yield prefix + page.url


def _output_sitemap_nested(
    sitemap: AbstractSitemap, strip_prefix: str = "", depth: int = 0
):
    sitemap_url = sitemap.url
    if depth != 0:
        sitemap_url = _strip_url(sitemap_url, strip_prefix)
    sys.stdout.write(tabs(depth) + sitemap_url + "\n")

    for sub_map in sitemap.sub_sitemaps:
        _output_sitemap_nested(sub_map, strip_prefix, depth + 1)

    for page in sitemap.pages:
        sys.stdout.write(tabs(depth + 1) + _strip_url(page.url, strip_prefix) + "\n")


def _output_pages(sitemap: AbstractSitemap, strip_prefix: str = ""):
    for page in sitemap.all_pages():
        sys.stdout.write(_strip_url(page.url, strip_prefix) + "\n")


def ls(args):
    tree = sitemap_tree_for_homepage(
        args.url,
        use_robots=not args.no_robots,
        use_known_paths=not args.no_known,
    )

    strip_prefix = ""
    if args.strip_url:
        strip_prefix = tree.url

    if args.format == "pages":
        _output_pages(tree, strip_prefix)
    elif args.format == "tabtree":
        _output_sitemap_nested(tree, strip_prefix)
    else:
        raise NotImplementedError(f"Format '{args.format}' not implemented")

    exit(0)
