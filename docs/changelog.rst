Changelog
=========

v1.0.0 (upcoming)
-----------------

- TODO

v0.6 (upcoming)
---------------

- Add proxy support with :meth:`.RequestsWebClient.set_proxies` (:pr:`20` by :user:`tgrandje`)
- Add additional sitemap discovery paths for news sitemaps (:commit:`d3bdaae56be87c97ce2f3f845087f495f6439b44`)
- Resolve warnings caused by :external+python:class:`http.HTTPStatus` usage (:commit:`3867b6e`)
- Don't add :class:`~.InvalidSitemap` object if ``robots.txt`` is not found (:pr:`39` by :user:`gbenson`)
- Add parameter to :meth:`~.RequestsWebClient.__init__` to disable certificate verification (:pr:`37` by :user:`japherwocky`)
- Remove log configuration so it can be specified at application level (:pr:`24` by :user:`dsoprea`)


Prior versions
--------------

For versions prior to 1.0, no changelog is available. Use the release tags to compare versions:

- `0.4...0.5 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.4...0.5>`__
- `0.3...0.4 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.3...0.4>`__
- `0.2...0.3 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.2...0.3>`__
- `0.1...0.2 <https://github.com/GateNLP/ultimate-sitemap-parser/compare/0.1...0.2>`__
