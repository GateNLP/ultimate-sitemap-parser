Supported Formats Reference
---------------------------

Overview of Parsers
===================

.. table::

    +-----------------------+-------------------------------------------------------+-----------------------------------------------------+---------------------------------------------------------------------------------------------------+
    | Format                | Index                                                                                                       | Pages                                                                                             |
    |                       +-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    |                       | Parser                                                | Object                                              | Parser                                           | Object                                         |
    +=======================+=======================================================+=====================================================+==================================================+================================================+
    | Website [*]_          |                                                       | :class:`~usp.objects.sitemap.IndexWebsiteSitemap`   |                                                  |                                                |
    +-----------------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    | `Robots.txt`_         | :class:`~usp.fetch_parse.IndexRobotsTxtSitemapParser` | :class:`~usp.objects.sitemap.IndexRobotsTxtSitemap` |                                                  |                                                |
    +-----------------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    | `Plain text`_         |                                                       |                                                     | :class:`~usp.fetch_parse.PlainTextSitemapParser` | :class:`~usp.objects.sitemap.PagesTextSitemap` |
    +-----------------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    | XML                   | :class:`~usp.fetch_parse.XMLSitemapParser`            |                                                     | :class:`~usp.fetch_parse.XMLSitemapParser`       |                                                |
    +-----+-----------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    |     | `Sitemap`_      | :class:`~usp.fetch_parse.IndexXMLSitemapParser`       | :class:`~usp.objects.sitemap.IndexXMLSitemap`       | :class:`~usp.fetch_parse.PagesXMLSitemapParser`  | :class:`~usp.objects.sitemap.PagesXMLSitemap`  |
    |     +-----------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    |     | `RSS 2.0`_      |                                                       |                                                     | :class:`~usp.fetch_parse.PagesRSSSitemapParser`  | :class:`~usp.objects.sitemap.PagesRSSSitemap`  |
    |     +-----------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    |     | `Atom 0.3/1.0`_ |                                                       |                                                     | :class:`~usp.fetch_parse.PagesAtomSitemapParser` | :class:`~usp.objects.sitemap.PagesAtomSitemap` |
    +-----+-----------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+
    | Unknown               |                                                       | :class:`~usp.objects.sitemap.InvalidSitemap`        |                                                  | :class:`~usp.objects.sitemap.InvalidSitemap`   |
    +-----------------------+-------------------------------------------------------+-----------------------------------------------------+--------------------------------------------------+------------------------------------------------+

.. [*] Represents the root of the website to allow for robots.txt and path-discovered sitemaps.


Robots.txt
==========

.. dropdown:: Example
    :class-container: flush

    .. literalinclude:: formats_examples/robots.txt
        :language: text

- `RFC 9309`_
- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt?hl=en>`__
- `Google library implementation <https://github.com/google/robotstxt>`__

The robots.txt parser implements the same logic to detect ``Sitemap`` keys as Google's parser, namely it is case insensitive and supports ``Sitemap`` or ``Site-map``.

Plain Text
==========

.. dropdown:: Example
    :class-container: flush

    .. literalinclude:: formats_examples/plaintext.txt
        :language: text

- `Sitemaps.org specification <https://sitemaps.org/protocol.html#otherformats>`__
- `Google documentation <https://developers.google.com/search/docs/advanced/sitemaps/build-sitemap#text>`__

The plain text parser reads the file line by line and considers anything that appears to be a useful URL a page. Specifically, it looks for lines that appear to be URLs, can be parsed successfully by :func:`python:urllib.parse.urlparse`, and have the HTTP or HTTPS protocol and has a non-empty hostname. This means that non-URLs in the file will simply be ignored, which is more permissive than the either standard.

.. _Sitemap:

XML Sitemap
===========

.. dropdown:: Examples
    :class-container: flush

    .. tab-set::

        .. tab-item:: Index

            .. literalinclude:: formats_examples/simple-index.xml
                :language: xml

        .. tab-item:: URL Set

            .. literalinclude:: formats_examples/simple-urlset.xml
                :language: xml

- `Sitemaps.org specification <https://sitemaps.org/protocol.html>`__
- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap#xml>`__

Sitemaps XML (not to be confused with other sitemap formats that happen to be in XML) is the most common kind of sitemap.

The Sitemaps XML parser supports both the Sitemap and Sitemap index formats.

Supports the following non-standard features:

- Truncated files (perhaps because the web server timed out while serving the file) will be parsed as much as possible
- Any unexpected tags are ignored
- Timestamps are :ref:`parsed flexibly <xml date>`

.. note::

    Namespaces must be declared to parse the sitemap and any extensions correctly. Any unrecognised namespaces will be ignored.

.. _xml sitemap extensions:

XML Sitemap Extensions
^^^^^^^^^^^^^^^^^^^^^^

- `Google documentation on combining sitemap extensions <https://developers.google.com/search/docs/crawling-indexing/sitemaps/combine-sitemap-extensions>`__

.. note::

    The `Google Video`_ extension is not currently supported, and only the standard part of the sitemap will be parsed.


.. _Google Video: https://developers.google.com/search/docs/crawling-indexing/sitemaps/video-sitemaps


.. _google-news-ext:

Google News
"""""""""""

- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap>`__


.. dropdown:: Example
    :class-container: flush

    .. literalinclude:: formats_examples/google-news.xml
        :emphasize-lines: 3,8-14,20-26
        :language: xml


The Google News extension provides additional information to describe the news story which a webpage represents, in addition to the page itself.

If the page contains Google News data, it is stored as a :class:`~usp.objects.page.SitemapNewsStory` object in :attr:`SitemapPage.news_story <usp.objects.page.SitemapPage.news_story>`.

Google Image
""""""""""""

- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps>`__

.. dropdown:: Example
    :class-container: flush

    .. literalinclude:: formats_examples/google-image.xml
        :emphasize-lines: 3,8-13,19-21
        :language: xml

The Google Image extension provides additional information to describe images on the page.

If the page contains Google Image data, it is stored as a list of :class:`~usp.objects.page.SitemapImage` objects in :attr:`SitemapPage.images <usp.objects.page.SitemapPage.images>`.

.. _xml date:

Date Time Parsing
^^^^^^^^^^^^^^^^^

It is relatively common for sitemaps to not correctly follow the `W3C Datetime`_ format (a subset of `ISO 8601`_). To handle this, date times are parsed flexibly with fallbacks. This is done in two steps to allow the faster, more reliable parser to be used where possible.

First, an attempt is made with a full ISO 8601 parser:

- In Python ≥ 3.11, :meth:`datetime.fromisoformat() <python:datetime.datetime.fromisoformat>` is tried first.
- In older versions [#dtvers]_, :meth:`dateutil:dateutil.parser.isoparse` is used

If this is unsuccessful, :meth:`dateutil:dateutil.parser.parse` is tried, which is able to parse most standard forms of date, but is slower and is more likely to mis-parse.

Without trying the optimised parser first, in large sitemaps, datetime parsing would take a significant proportion of the total runtime.

RSS 2.0
=======

.. dropdown:: Example
    :class-container: flush

    .. literalinclude:: formats_examples/rss2.0.xml
        :language: xml

- `RSS 2.0 specification <https://www.rssboard.org/rss-specification>`__
- `Sitemaps.org specification <https://www.sitemaps.org/protocol.html#otherformats>`__
- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap#rss>`__

Implementation details:

- Per the specification, ``<item>`` elements without a ``<title>`` or ``<description>`` are invalid and ignored.
- Although the specification states ``<link>`` is optional, we ignore an ``<item>`` if it does not contain one
- Dates are parsed flexibly

.. note::

    `mRSS <https://www.rssboard.org/media-rss>`_ is not currently supported and will be ignored.

.. _rss date:

Date Time Parsing
^^^^^^^^^^^^^^^^^

It is relatively common for feeds to not correctly follow the `RFC 2822`_ format. To handle this, date times are parsed with :meth:`dateutil:dateutil.parser.parse`, which is able to parse most standard forms of date. Given that feeds should be short, the performance impact of this is minimal.


Atom 0.3/1.0
============

.. dropdown:: Examples
    :class-container: flush

    .. tab-set::

        .. tab-item:: Atom 0.3

            .. literalinclude:: formats_examples/atom0.3.xml
                :language: xml

        .. tab-item:: Atom 1.0

            .. literalinclude:: formats_examples/atom1.0.xml
                :language: xml

- `Atom 0.3 specification <https://web.archive.org/web/20060811235523/http://www.mnot.net/drafts/draft-nottingham-atom-format-02.html>`__
- `Atom 1.0 specification <https://www.rfc-editor.org/rfc/rfc4287.html>`__
- `Moving from Atom 0.3 to 1.0 <https://web.archive.org/web/20090717114706/http://rakaz.nl/2005/07/moving-from-atom-03-to-10.html>`__ by Niels Leenheer
- `Google documentation <https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap#rss>`__

Implementation details:

- The same parser is used for 0.3 and 1.0, and it does not attempt to detect the version, therefore it can accept invalid feeds which are a mixture of both
- Dates are parsed flexibly

.. _atom date:

Date Time Parsing
^^^^^^^^^^^^^^^^^

Atom 0.3 follows the `W3C Datetime`_ (a subset of `ISO 8601`_) format, and Atom 1.0 follows `RFC 3339`_ (which is similar but not entirely equivalent to ISO 8601 [#3339-8601-diff]_). In either case, :meth:`dateutil:dateutil.parser.parse` is used to parse the date, which is able to parse most standard forms of date. Given that feeds should be short, the performance impact of this is minimal.


.. rubric:: Footnotes

.. [#dtvers] Prior to Python 3.11, :meth:`datetime.fromisoformat() <python:datetime.datetime.fromisoformat>` could only parse times in the specific ISO 8601 format emitted by :meth:`datetime.isoformat() <python:datetime.datetime.isoformat>` so is unsuitable as a general parser.
.. [#3339-8601-diff] See `this page <https://ijmacd.github.io/rfc3339-iso8601/>`_ for some examples.

.. _W3C Datetime: https://www.w3.org/TR/NOTE-datetime
.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
.. _RFC 3339: https://www.rfc-editor.org/rfc/rfc3339.html
.. _RFC 2822: https://www.rfc-editor.org/rfc/rfc2822.html#page-14
.. _RFC 9309: https://www.rfc-editor.org/rfc/rfc9309.html