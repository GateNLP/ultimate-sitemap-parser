.. image:: https://travis-ci.org/berkmancenter/mediacloud-ultimate_sitemap_parser.svg?branch=develop
    :target: https://travis-ci.org/berkmancenter/mediacloud-ultimate_sitemap_parser
    :alt: Build Status

.. image:: https://readthedocs.org/projects/ultimate-sitemap-parser/badge/?version=latest
    :target: https://ultimate-sitemap-parser.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/berkmancenter/mediacloud-ultimate_sitemap_parser/badge.svg?branch=develop
    :target: https://coveralls.io/github/berkmancenter/mediacloud-ultimate_sitemap_parser?branch=develop
    :alt: Coverage Status

.. image:: https://badge.fury.io/py/ultimate-sitemap-parser.svg
    :target: https://badge.fury.io/py/ultimate-sitemap-parser
    :alt: PyPI package


Website sitemap parser for Python 3.5+.


Features
========

- Supports all sitemap formats:

  - `XML sitemaps <https://www.sitemaps.org/protocol.html#xmlTagDefinitions>`_
  - `Google News sitemaps <https://support.google.com/news/publisher-center/answer/74288?hl=en>`_
  - `plain text sitemaps <https://www.sitemaps.org/protocol.html#otherformats>`_
  - `RSS 2.0 / Atom 0.3 / Atom 1.0 sitemaps <https://www.sitemaps.org/protocol.html#otherformats>`_
  - `robots.txt sitemaps <https://developers.google.com/search/reference/robots_txt#sitemap>`_

- Field-tested with ~1 million URLs as part of the `Media Cloud project <https://mediacloud.org/>`_
- Error-tolerant with more common sitemap bugs
- Tries to find sitemaps not listed in ``robots.txt``
- Uses fast and memory efficient Expat XML parsing
- Provides a generated sitemap tree as easy to use object tree
- Supports using a custom web client
- Uses a small number of actively maintained third-party modules
- Reasonably tested


Installation
============

.. code:: sh

    pip install ultimate_sitemap_parser


Usage
=====

.. code:: python

    from usp.tree import sitemap_tree_for_homepage

    tree = sitemap_tree_for_homepage('https://www.nytimes.com/')
    print(tree.all_pages())

Check out the `API reference in the documentation <https://ultimate-sitemap-parser.readthedocs.io/en/latest/>`_ for more details.

