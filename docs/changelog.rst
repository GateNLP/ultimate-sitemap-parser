Changelog
=========

v1.1.2 (upcoming)
-----------------

**New Features**

- Support passing additional known sitemap paths to `sitemap_tree_for_homepage` (:pr:`69`)

v1.1.1 (2025-01-29)
-------------------

**Bug Fixes**

- Changed log level when a suspected gzipped sitemap can't be un-gzipped from `error` to `warning`, since parsing can usually continue (:pr:`62` by :user:`redreceipt`)
- Line references in logs now reference the correct location instead of lines within the logging helper file (:pr:`63`)

v1.1.0 (2025-01-20)
-------------------

**New Features**

* Added support for :ref:`alternate localised pages <sitemap-extra-localisation>` with ``hreflang``.
* If an HTTP error is encountered, the contents of the error page is logged at ``INFO`` level.
* Added optional configurable wait time to HTTP request client.

v1.0.0 (2025-01-13)
-------------------

Ultimate Sitemap Parser is now maintained by the `GATE Team <https://gate.ac.uk/>`_ at the School of Computer Science, University of Sheffield. We'd like to thank Linas Valiukas and Hal Roberts for their work on this package, and Paige Gulley for coordinating the transfer of the library.

**Breaking Changes**

* Python v3.8 is now the lowest supported version of Python. Future releases will follow `Python's version support <https://devguide.python.org/versions/>`_.

**New Features**

* CLI tool to parse and list sitemaps on the command line (see :doc:`/reference/cli`)
* All sitemap objects now implement a consistent interface, allowing traversal of the tree irrespective of type:

  * All sitemaps now have ``pages`` and ``sub_sitemaps`` properties, returning their children of that type, or an empty list where not applicable
  * Added ``all_sitemaps()`` method to iterate over all descendant sitemaps

* Pickling page sitemaps now includes page data, which previously was not included as it was swapped to disk
* Sitemaps and pages now implement ``to_dict()`` method to convert to dictionaries (requested in :issue:`18`)
* Added optional arguments to ``usp.tree.sitemap_tree_for_homepage()`` to disable robots.txt-based or known-path-based sitemap discovery. Default behaviour is still to use both.
* Parse sitemaps from a string with :ref:`local parse` (requested in :issue:`26`)
* Support for the Google Image sitemap extension
* Add proxy support with ``RequestsWebClient.set_proxies()`` (:pr:`20` by :user:`tgrandje`)
* Add additional sitemap discovery paths for news sitemaps (:commit:`d3bdaae56be87c97ce2f3f845087f495f6439b44`)
* Add parameter to ``RequestsWebClient.__init__()`` to disable certificate verification (:pr:`37` by :user:`japherwocky`)

**Performance**

Improvement of parse performance by approximately 90%:

* Optimised lookup of page URLs when checking if duplicate
* Optimised datetime parse in XML Sitemaps by trying full ISO8601 parsers before the general parser

**Bug Fixes**

* Invalid datetimes will be parsed as ``None`` instead of crashing (reported in :issue:`22`, :issue:`31`)
* Invalid priorities will be set to the default (0.5) instead of crashing
* Moved ``__version__`` attribute into main class module
* Robots.txt index sitemaps now count for the max recursion depth (reported in :issue:`29`). The default maximum has been increased by 1 to compensate for this.
* Remove log configuration so it can be specified at application level (reported in :issue:`25`, :pr:`24` by :user:`dsoprea`/:user:`antonialoytorrens-ikaue`)
* Resolve warnings caused by :external+python:class:`http.HTTPStatus` usage (:commit:`3867b6e`)
* Don't add ``InvalidSitemap`` object if ``robots.txt`` is not found (:pr:`39` by :user:`gbenson`)
* Fix incorrect lowercasing of URLS discovered in robots.txt (reported in :issue:`40`, :pr:`35` by :user:`ArthurMelin`)


Prior versions
--------------

For versions prior to 1.0, no changelog is available. Use the release tags to compare versions:

* `0.4...0.5 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.4...0.5>`__
* `0.3...0.4 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.3...0.4>`__
* `0.2...0.3 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.2...0.3>`__
* `0.1...0.2 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.1...0.2>`__
