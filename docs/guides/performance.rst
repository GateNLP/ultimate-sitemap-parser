Performance
===========

USP is able to parse even very large and complex sitemaps very quickly and in a memory-efficient fashion.

As an example, USP is able to parse the sitemap of the BBC website, which contains 2.6m URLS across 75 sitemaps, in less than a minute (excluding HTTP test times), and using approximately 90MiB of memory at peak.


XML Parse Efficiency
--------------------

For XML documents, USP uses the :external+python:doc:`Expat parser <library/pyexpat>` for high performance parsing of documents without requiring them to be strictly correct. As it is a stream-based parser, USP is able to hook its sitemap parsing into the XML parse process, opposed to having to parse the entire document and then work on the parse tree.

Memory Efficiency
-----------------

When constructing the :ref:`sitemap-page tree <process_tree_construction>` only the sitemap part of the tree is constantly stored in memory. During instantiation of the :class:`~usp.objects.sitemap.AbstractPagesSitemap`, page data is swapped into a temporary file on disk, and only loaded into memory when its pages are accessed.

.. _performance_page_generator:

Page Generator
^^^^^^^^^^^^^^

Due to the swapping process, it is most efficient to use the iterator returned by :func:`~usp.objects.sitemap.AbstractSitemap.all_pages` directly. This will load one sitemap's pages into memory at once, rather than all simultaneously.

.. grid:: 1 1 2 2
    :padding: 0

    .. grid-item-card::
        :class-item: code-card
        :class-header: sd-bg-success sd-bg-text-success sd-outline-success
        :class-card: sd-outline-success

        :octicon:`check` Good Practice
        ^^^^

        .. code-block::

            for page in tree.all_pages():
                print(page.url)

    .. grid-item-card::
        :class-item: code-card
        :class-header: sd-bg-warning sd-bg-text-warning sd-outline-warning
        :class-card: sd-outline-warning

        :octicon:`alert` Avoid
        ^^^

        .. code-block::

            for page in list(tree.all_pages()):
                print(page.url)

Of course, in some cases, this is unavoidable. Even so, USP is still relatively memory efficient - for the BBC website the entire page list consumes approximately 560MiB of memory (compared to the plaintext files which are approximately 370MiB).