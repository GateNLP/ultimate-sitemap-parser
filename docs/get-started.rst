Get Started
===========

Ultimate Sitemap Parser can be installed from PyPI or conda-forge:

.. tab-set::

    .. tab-item:: pip

        .. code-block:: shell-session

            $ pip install ultimate-sitemap-parser

    .. tab-item:: conda

        .. code-block:: shell-session

            $ conda install -c conda-forge ultimate-sitemap-parser


Traversing a website's sitemaps and retrieving all webpages requires just a single line of code:

.. code-block:: python

    from usp.tree import sitemap_tree_for_homepage

    tree = sitemap_tree_for_homepage('https://example.org/')

This will return a tree representing the structure of the sitemaps. To iterate through the pages, use :func:`tree.all_pages() <usp.objects.sitemap.AbstractSitemap.all_pages>`.

.. code-block:: python

    for page in tree.all_pages():
        print(page.url)

This will output the URL of each page in the sitemap, loading the parsed representations of sitemaps `lazily to reduce memory usage <performance_page_generator>`_ in very large sitemaps.

Each page is an instance of :class:`~usp.objects.page.SitemapPage`, which will always have at least a URL and priority, and may have other attributes if present.
