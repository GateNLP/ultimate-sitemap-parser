Sitemap Tree
============

Calling :func:`~usp.tree.sitemap_tree_for_homepage` will return the root node of a tree representing the structure of the sitemaps found on a website.

Index vs Page Sitemaps
----------------------

A small site may just have a single sitemap hosted at ``/sitemap.xml``, but larger sites often use a more complex structure. By convention, sitemaps are limited to 50,000 URLs or 50MB each, so large sites will have to split sitemaps. It's also common to split sitemaps semantically, such as by language or content type.

Sitemaps are divided into two types:

- **Index sitemaps** list other sitemaps, which may themselves be index sitemaps or page sitemaps
- **Page sitemaps** list pages

On a more complex site, in order to find all pages, you would have to fetch the index sitemaps (potentially several levels deep) and then fetch the page sitemaps they reference.

Basic Examples
--------------

A small site with a single sitemap located at ``/sitemap.xml`` would look like this:

.. note::

    In diagrams like these, square boxes represent index sitemaps and rounded boxes represent page sitemaps. In reality, each page-type sitemap will have a list of pages as its children, but these are omitted for brevity.

    Nodes are clickable to access the documentation for that class.

.. graphviz::
    :name: fig-simple-sitemap
    :align: center

    digraph G {
        root [
            shape=record,
            xref=":class:`~usp.objects.sitemap.IndexWebsiteSitemap`",
            label="{IndexWebsiteSitemap|/}"
        ]
        sitemap [
            shape=record,
            xref=":class:`~usp.objects.sitemap.PagesXMLSitemap`",
            label="{PagesXMLSitemap|/sitemap.xml}",
            style=rounded
        ]
        sitemap_p [label="Pages", shape=plain]
        root -> sitemap -> sitemap_p
    }

In this case, the sitemap was discovered because it was at a well-known URL. USP has a built-in list (:data:`usp.tree._UNPUBLISHED_SITEMAP_PATHS`) of common sitemap locations to check.

Additionally, USP checks the site's ``robots.txt`` file for a sitemap directive. Had the sitemap been declared in ``robots.txt`` instead, the tree would look like this:

.. graphviz::
    :name: fig-simple-robots
    :align: center

    digraph G {
        root [
            shape=record,
            xref=":class:`~usp.objects.sitemap.IndexWebsiteSitemap`",
            label="{IndexWebsiteSitemap|/}"
        ]
        robots [
            shape=record,
            xref=":class:`~usp.objects.sitemap.IndexRobotsTxtSitemap`",
            label="{IndexRobotsTxtSitemap|/robots.txt}"
        ]
        sitemap [
            shape=record,
            xref=":class:`~usp.objects.sitemap.PagesXMLSitemap`",
            label="{PagesXMLSitemap|/sitemap.xml}",
            style=rounded
        ]
        sitemap_p [label="Pages", shape=plain]
        root -> robots -> sitemap -> sitemap_p
    }

The sitemap is now a child of the ``robots.txt`` file (which we treat as a type of index sitemap) because it's queried first, and well-known URLs are skipped if they've already been retrieved through ``robots.txt``.

Finally, in this third example, the site has sitemaps listed in ``robots.txt`` and some additional sitemaps at well-known URLs:

.. graphviz::
    :name: fig-sitemap-hierarchy
    :align: center

    digraph G {
        node [shape=record];
        root [
            xref=":class:`~usp.objects.sitemap.IndexWebsiteSitemap`",
            label="{IndexWebsiteSitemap|/}"
        ]

        root -> robots

        robots [
            xref=":class:`~usp.objects.sitemap.IndexRobotsTxtSitemap`",
            label="{IndexRobotsTxtSitemap|/robots.txt}"
        ]

        sitemap [
            xref=":class:`~usp.objects.sitemap.PagesXMLSitemap`",
            label="{PagesXMLSitemap|/sitemap.xml}",
            style=rounded
        ]
        sitemap_p [label="Pages", shape=plain]
        robots -> sitemap -> sitemap_p

        root -> news_index
        news_index [
            xref=":class:`~usp.objects.sitemap.IndexXMLSitemap`",
            label="{IndexXMLSitemap|/sitemap_news.xml}"
        ]
        news_1 [
            xref=":class:`~usp.objects.sitemap.AbstractPagesSitemap`",
            label="{PagesXMLSitemap|/sitemap_news_1.xml}",
            style=rounded
        ]
        news_1p [label="Pages", shape=plain]
        news_index -> news_1 -> news_1p
        news_2 [
            xref=":class:`~usp.objects.sitemap.PagesXMLSitemap`"
            label="{PagesXMLSitemap|/sitemap_news_2.xml}",
            style=rounded
            ]
        news_2p [label="Pages", shape=plain]
        news_index -> news_2 -> news_2p
        news_3 [
            xref=":class:`~usp.objects.sitemap.PagesXMLSitemap`",
            label="{PagesXMLSitemap|/sitemap_news_3.xml}",
            style=rounded
        ]
        news_3p [label="Pages", shape=plain]
        news_index -> news_3 -> news_3p
    }

Here, ``sitemap_news.xml`` is an example of an XML index sitemap, which contains no pages itself, but just points to 3 sub-sitemaps. It should also be clearer from this example why it's necessary to add the root node to combine the sitemaps found from ``robots.txt`` and well-known URLs.

Sitemap trees will always have an :class:`~.IndexWebsiteSitemap` at the root, and will usually consist of :class:`~.IndexXMLSitemap` and :class:`~.PagesXMLSitemap` (either directly or through a :class:`~.IndexRobotsTxtSitemap`), but :doc:`other sitemap types are possible </reference/formats>`. Regardless, all sitemap classes implement the same interface (:class:`~.AbstractIndexSitemap` or :class:`~.AbstractPagesSitemap`, which both inherit from :class:`~.AbstractSitemap`), so the actual type of sitemap is not important for most use cases.


Real-World Example
------------------

Large and well-established sites (e.g. media outlets) may have very complex sitemap hierarchies, due to the amount of content and changing technologies for the site. For example, this is the sitemap hierarchy for the BBC website:

.. dropdown:: bbc.co.uk Sitemap Graph

    .. graphviz:: _sitemap_examples/bbc-sitemap.dot

Altogether, this sitemap tree contains 2.6 million URLs spread across 75 sitemaps. The ``robots.txt`` file declares 13 sitemaps, some of which are index sitemaps with as many as 50 page sitemaps. Despite this, USP is able to parse this tree in less than a minute and using no more than 90MiB of memory at peak.


Note also that there is some duplication in this tree. The sitemap ``/sport/sitemap.xml`` is both directly declared in ``robots.txt`` and also in the index sitemap ``/sitemap.xml``. As these declarations are in different sitemap files, they are both included in the tree. Likewise, the pages declared in the ``/sport/sitemap.xml`` file are included in the tree twice. See the section on :ref:`process_dedup` for details.

Traversal
---------

To traverse the sitemaps and pages in the tree, :class:`~usp.objects.sitemap.AbstractSitemap` declares an interface to access the immediate children of a sitemap node through properties, or all descendants through methods.

These methods and properties are always implemented, returning or yielding empty lists where not applicable (e.g. accessing sub-sitemaps on a page sitemap, or either sub-sitemaps or pages on an invalid sitemap), meaning they can be called without checking the type of the sitemap.

For sub-sitemaps:

- :attr:`AbstractSitemap.sub_sitemaps <usp.objects.sitemap.AbstractSitemap.sub_sitemaps>` is a list of the direct children of that sitemap
- :meth:`AbstractSitemap.all_sitemaps() <usp.objects.sitemap.AbstractSitemap.all_sitemaps>` returns an iterator yielding all descendant sitemaps (depth-first)

For pages:

- :attr:`AbstractSitemap.pages <usp.objects.sitemap.AbstractSitemap.pages>` is a list of the direct children of that sitemap
- :meth:`AbstractSitemap.all_pages() <usp.objects.sitemap.AbstractSitemap.all_pages>` returns an iterator yielding all descendant pages (depth-first)
