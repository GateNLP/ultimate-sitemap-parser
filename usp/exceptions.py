"""Exceptions used by the sitemap parser."""


class SitemapException(Exception):
    """
    Problem due to which we can't run further, e.g. wrong input parameters.
    """

    pass


class SitemapXMLParsingException(Exception):
    """
    XML parsing exception to be handled gracefully.
    """

    pass


class GunzipException(Exception):
    """
    Error decompressing seemingly gzipped content.
    See :func:`usp.helpers.gunzip`.
    """

    pass


class StripURLToHomepageException(Exception):
    """
    Problem parsing URL and stripping to homepage.
    See :func:`usp.helpers.strip_url_to_homepage`.
    """

    pass
