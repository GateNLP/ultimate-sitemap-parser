Changelog
=========

v1.0.0 (upcoming)
-----------------

**New Features**

- CLI tool to parse and list sitemaps on the command line (see :doc:`/reference/cli`)
- All sitemap objects now implement a consistent interface, allowing traversal of the tree irrespective of type:
    - All sitemaps now have ``pages`` and ``sub_sitemaps`` properties, returning their children of that type, or an empty list where not applicable
    - Added ``all_sitemaps()`` method to iterate over all descendant sitemaps
- Pickling page sitemaps now includes page data, which previously was not included as it was swapped to disk
- Sitemaps and pages now implement ``to_dict()`` method to convert to dictionaries
- Added optional arguments to ``usp.tree.sitemap_tree_for_homepage()`` to disable robots.txt-based or known-path-based sitemap discovery. Default behaviour is still to use both.
- Parse sitemaps from a string with :ref:`local parse`

**Performance**

Improvement of parse performance by approximately 90%:

- Optimised lookup of page URLs when checking if duplicate
- Optimised datetime parse in XML Sitemaps by trying full ISO8601 parsers before the general parser

**Bug Fixes**

- Invalid datetimes will be parsed as ``None`` instead of crashing (reported in :issue:`22`, :issue:`31`)
- Moved ``__version__`` attribute into main class module
- Robots.txt index sitemaps now count for the max recursion depth (reported in :issue:`29`). The default maximum has been increased by 1 to compensate for this.

v0.6 (upcoming)
---------------

**New Features**

- Add proxy support with ``RequestsWebClient.set_proxies()`` (:pr:`20` by :user:`tgrandje`)
- Add additional sitemap discovery paths for news sitemaps (:commit:`d3bdaae56be87c97ce2f3f845087f495f6439b44`)
- Add parameter to ``RequestsWebClient.__init__()`` to disable certificate verification (:pr:`37` by :user:`japherwocky`)

**Bug Fixes**

- Remove log configuration so it can be specified at application level (:pr:`24` by :user:`dsoprea`)
- Resolve warnings caused by :external+python:class:`http.HTTPStatus` usage (:commit:`3867b6e`)
- Don't add ``InvalidSitemap`` object if ``robots.txt`` is not found (:pr:`39` by :user:`gbenson`)
- Fix incorrect lowercasing of URLS discovered in robots.txt (:pr:`35`)

Prior versions
--------------

For versions prior to 1.0, no changelog is available. Use the release tags to compare versions:

- `0.4...0.5 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.4...0.5>`__
- `0.3...0.4 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.3...0.4>`__
- `0.2...0.3 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.2...0.3>`__
- `0.1...0.2 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.1...0.2>`__
