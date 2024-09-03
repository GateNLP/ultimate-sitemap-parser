:hide-toc:

Ultimate Sitemap Parser
=======================

.. toctree::
    :hidden:

    get-started

.. toctree::
    :hidden:
    :caption: Guides

    guides/sitemap-tree
    guides/fetch-parse
    guides/saving
    guides/performance
    guides/security

.. toctree::
    :hidden:
    :caption: Reference

    Supported Formats <reference/formats>
    Python API <reference/api/index>
    CLI <reference/cli>

.. toctree::
    :hidden:
    :caption: About

    changelog
    acknowledgements
    GitHub <https://github.com/GateNLP/ultimate-sitemap-parser>
    PyPI <https://pypi.org/project/ultimate-sitemap-parser>
    Issues <https://github.com/GateNLP/ultimate-sitemap-parser/issues>



Ultimate Sitemap Parser (USP) is a performant and robust Python library for parsing and crawling sitemaps.

- **Supports all sitemap formats**: Sitemap XML, Google News, plain text, RSS 2.0, Atom 0.3/1.0.

- **Error-tolerant**: Handles common sitemap bugs gracefully.

- **Automatic sitemap discovery**: Finds sitemaps from *robots.txt* and from common sitemap names.

- **Fast and memory efficient**: Uses Expat XML parsing, doesn't consume much memory even with massive sitemap hierarchies. Swaps and lazily loads sub-sitemaps to disk.

- **Field-tested with ~1 million URLs**: Originally developed for the `Media Cloud <https://mediacloud.org/>`_ project where it was used to parse approximately 1 million sitemaps.


Installation
------------

Ultimate Sitemap Parser can be installed from PyPI or conda-forge:

.. tab-set::

    .. tab-item:: pip

        .. code-block:: shell-session

            $ pip install ultimate-sitemap-parser

    .. tab-item:: conda

        .. code-block:: shell-session

            $ conda install -c conda-forge ultimate-sitemap-parser

Usage
-----

USP is very easy to use, with just a single line of code it can traverse and parse a website's sitemaps:

.. code-block:: python

    from usp.tree import sitemap_tree_for_homepage

    tree = sitemap_tree_for_homepage('https://www.example.org/')

    for page in tree.all_pages():
        print(page.url)

Advanced Features
-----------------

- :doc:`CLI Client <reference/cli>`: Use the ``usp ls`` tool to work with sitemaps from the command line.
- :doc:`Serialisation <guides/saving>`: Export raw data or save to disk and load later
- Custom web clients: Instead of the default client built on `requests <https://requests.readthedocs.io/en/latest/>`_ you can use your own web client by implementing the :class:`~usp.web_client.abstract_client.AbstractWebClient` interface.