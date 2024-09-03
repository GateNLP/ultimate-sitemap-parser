Fetch and Parse Process
=======================

When calling :func:`~usp.tree.sitemap_tree_for_homepage`, USP will try several methods to find sitemaps and recurse through sub-sitemaps.

Broadly the process is as follows:

1. Attempt to fetch ``https://example.org/robots.txt`` and parse for ``Sitemap:`` statements. We consider ``robots.txt`` to be an index-type sitemap (as it lists other sitemaps)
2. Fetch and parse each discovered sitemap URL. If a sitemap is an index-type sitemap, recurse into it.
3. Try to fetch known sitemap locations like ``/sitemap.xml`` and ``/sitemap_index.xml``, excluding those already declared in ``robots.txt``.
4. Create a top-level dummy sitemap to act as the parent of ``robots.txt`` and discovered sitemaps.

.. seealso::
    :class: sidebar

    :doc:`Reference of formats, parsing and representation classes </reference/formats>`

All fetching is done through the :class:`~usp.fetch_parse.SitemapFetcher` class, which is responsible for fetching and choosing the appropriate parser for the content.

The fetcher then attempts to parse using the process shown in this flowchart:

.. dropdown:: Show Parse Flowchart
    :icon: workflow
    :name: fig-parse-flow

    .. graphviz:: parse_flow.dot

Non-XML documents are parsed directly with their respective parser. For XML documents, the :class:`~usp.fetch_parse.XMLSitemapParser` parses the document to determine the type of the XML document and select the appropriate parser (the *concrete parser*) to actually extract information.

XML documents are detected with a heuristic (the document, when leading whitespace is trimmed, starts with ``<``) to avoid issues with incorrect content types.

Index-type parsers instantiate the appropriate class from :mod:`usp.objects.sitemap` and another :class:`~usp.fetch_parse.SitemapFetcher` to fetch each of their children. This allows a sitemap of one type (e.g. robots.txt) to contain sitemaps of another type (e.g. XML). Duplicate declarations of sub-sitemaps within the same index-type sitemap are ignored, but otherwise order is preserved.

Page-type parsers instantiate the appropriate class from :mod:`usp.objects.sitemap` and instantiate instances of their internal page class (e.g. :class:`PagesXMLSitemapParser.Page <usp.fetch_parse.PagesXMLSitemapParser.Page>`). These are not converted to the public class :class:`~usp.objects.page.SitemapPage` until the end of the fetch process. The order sub-sitemaps or pages are declare in is preserved.


.. _process_tree_construction:

Tree Construction
-----------------

.. seealso::

    :doc:`/guides/sitemap-tree`

Each parser instance returns an object inheriting from :class:`~usp.objects.sitemap.AbstractSitemap` after the parse process (including any child fetch-and-parses), constructing the tree from the bottom up. The top :class:`~usp.objects.sitemap.IndexWebsiteSitemap` is then created to act as the parent of ``robots.txt`` and all well-known-path discovered sitemaps.

.. _process_dedup:

Deduplication
-------------

During the parse process, some de-duplication is performed within each individual sitemap. In an index sitemap, only the first declaration of a sub-sitemap is fetched. In a page sitemap, only the first declaration of a page is included.

However, this means that if a sub-sitemap is declared in multiple index sitemaps, or a page is declared in multiple page sitemaps, it will be included multiple times.

