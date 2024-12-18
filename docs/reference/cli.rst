.. _cli:

CLI Reference
-------------

The CLI provides a simple command-line interface to retrieve sitemap data.

``usp``
=======

.. code-block:: none

    usage: usp [-h] [-v]  ...

    Ultimate Sitemap Parser

    options:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit

    commands:

        ls           List sitemap pages

``usp ls``
==========

.. code-block:: none

    usage: usp ls [-h] [-f] [-r] [-k] [-u] url

    download, parse and list the sitemap structure

    positional arguments:
      url              URL of the site including protocol

    options:
      -h, --help       show this help message and exit
      -f , --format    set output format (default: tabtree)
                       choices:
                         tabtree: Sitemaps and pages, nested with tab indentation
                         pages: Flat list of pages, one per line
      -r, --no-robots  don't discover sitemaps through robots.txt
      -k, --no-known   don't discover sitemaps through well-known URLs
      -u, --strip-url  strip the supplied URL from each page and sitemap URL

.. rubric:: Examples

.. code-block:: shell-session

    $ usp ls https://example.org/
    https://example.org/
        https://example.org/robots.txt
            https://example.org/sitemap.xml
                https://example.org/page1.html


.. code-block:: shell-session

    $ usp ls https://example.org/ --strip-url
    https://example.org/
        /robots.txt
            /sitemap.xml
                /page1.html

.. code-block:: shell-session

    $ usp ls https://example.org/ --format pages
    https://example.org/page1.html