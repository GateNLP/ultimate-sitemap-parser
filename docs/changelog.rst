Changelog
=========

v1.6.0 (2025-09-10)
-------------------

**New Features**

* Added ``recurse_callback`` and ``recurse_list_callback`` parameters to ``usp.tree.sitemap_tree_for_homepage`` to filter which sub-sitemaps are recursed into (:pr:`106` by :user:`nicolas-popsize`)


**Bug Fixes**

* If a `FileNotFoundError` is encountered when cleaning up a sitemap page temporary file, it will now be caught and logged as a warning. (:pr:`108`)

  * This resolves an error which we believe only occurs on Windows in complex environments (e.g. when running the full Pytest suite)

v1.5.0 (2025-08-11)
-------------------

**Bug Fixes**

- Set different timeouts for HTTP request connection and read to lower maximum request length. Instead of 60s for each, it is now 9.05s for connection and 60s for read. (:pr:`95`)

v1.4.0 (2025-04-23)
-------------------

**New Features**

- Support parsing sitemaps when a proper XML namespace is not declared (:pr:`87`)

**Bug Fixes**

- Fix incorrect logic in gunzip behaviour which attempted to gunzip responses that were already gunzipped by requests (:pr:`89`)
- Change log output for gunzip failures to include the URL instead of request response object (:pr:`89`)

v1.3.1 (2025-03-31)
-------------------

**Bug Fixes**

- Fixed an issue with temporary file handling, which would cause USP to always crash on Windows (:pr:`84`)

v1.3.0 (2025-03-17)
-------------------

*This release drops support for Python 3.8. The minimum supported version is now Python 3.9.*

**New Features**

- Recursive sitemaps are detected and will return an ``InvalidSitemap`` instead (:pr:`74`)
- Known sitemap paths will be skipped if they redirect to a sitemap already found (:pr:`77`)
- The reported URL of a sitemap will now be its actual URL after redirects (:pr:`74`)
- Log level in CLI can now be changed with the ``-v`` or ``-vv`` flags, and output to a file with ``-l`` (:pr:`76`)
- When fetching known sitemap paths, 404 errors are now logged at a lower level (:pr:`78`)

**Bug Fixes**

- Some logging at ``INFO`` level has been changed to ``DEBUG`` (:pr:`76`)

**API Changes**

- Added ``AbstractWebClient.url()`` method to return the actual URL fetched after redirects. Custom web clients will need to implement this method.

v1.2.0 (2025-02-18)
-------------------

**New Features**

- Support passing additional known sitemap paths to ``usp.tree.sitemap_tree_for_homepage`` (:pr:`69`)
- The requests web client now creates a session object for better performance, which can be overridden by the user (:pr:`70`)

**Documentation**

- Added improved documentation for customising the HTTP client.

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
