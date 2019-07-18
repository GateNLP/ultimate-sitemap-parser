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
    gunzip() exception.
    """
    pass


class StripURLToHomepageException(Exception):
    """
    strip_url_to_homepage() exception.
    """
    pass
