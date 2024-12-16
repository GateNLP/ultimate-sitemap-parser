.. image:: https://travis-ci.org/mediacloud/ultimate-sitemap-parser.svg?branch=develop
    :target: https://travis-ci.org/mediacloud/ultimate-sitemap-parser
    :alt: Build Status

.. image:: https://readthedocs.org/projects/ultimate-sitemap-parser/badge/?version=latest
    :target: https://ultimate-sitemap-parser.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/ultimate-sitemap-parser.svg
    :target: https://badge.fury.io/py/ultimate-sitemap-parser
    :alt: PyPI package

.. image:: https://img.shields.io/conda/v/conda-forge/ultimate-sitemap-parser?color=brightgreen
   :target: https://anaconda.org/conda-forge/ultimate-sitemap-parser
   :alt: Conda

.. image:: https://pepy.tech/badge/ultimate-sitemap-parser
    :target: https://pepy.tech/project/ultimate-sitemap-parser
    :alt: Download stats


Ultimate Sitemap Parser (USP) is a performant and robust Python library for parsing and crawling sitemaps.

Features
========

- Supports all sitemap formats:

  - `XML sitemaps <https://www.sitemaps.org/protocol.html#xmlTagDefinitions>`_
  - `Google News sitemaps <https://support.google.com/news/publisher-center/answer/74288?hl=en>`_
  - `plain text sitemaps <https://www.sitemaps.org/protocol.html#otherformats>`_
  - `RSS 2.0 / Atom 0.3 / Atom 1.0 sitemaps <https://www.sitemaps.org/protocol.html#otherformats>`_
  - `Sitemaps linked from robots.txt <https://developers.google.com/search/reference/robots_txt#sitemap>`_

- Field-tested with ~1 million URLs as part of the `Media Cloud project <https://mediacloud.org/>`_
- Error-tolerant with more common sitemap bugs
- Tries to find sitemaps not listed in ``robots.txt``
- Uses fast and memory efficient Expat XML parsing
- Doesn't consume much memory even with massive sitemap hierarchies
- Provides a generated sitemap tree as easy to use object tree
- Supports using a custom web client
- Uses a small number of actively maintained third-party modules
- Reasonably tested


Installation
============

.. code:: sh

    pip install ultimate-sitemap-parser

or using Anaconda:

.. code:: sh

    conda install -c conda-forge ultimate-sitemap-parser


Usage
=====

.. code:: python

    from usp.tree import sitemap_tree_for_homepage

    tree = sitemap_tree_for_homepage('https://www.example.org/')

    for page in tree.all_pages():
        print(page.url)

``sitemap_tree_for_homepage()`` will return a tree of ``AbstractSitemap`` subclass objects that represent the sitemap
hierarchy found on the website; see a `reference of AbstractSitemap subclasses <https://ultimate-sitemap-parser.readthedocs.io/en/latest/reference/api/usp.objects.sitemap.html>`_. `AbstractSitemap.all_pages()` returns a generator to efficiently iterate over pages without loading the entire tree into memory.

For more examples and details, see the `documentation <https://ultimate-sitemap-parser.readthedocs.io/en/latest/>`_.

