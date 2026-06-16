Security
========

There is inherently some risk in downloading untrusted content from the web and parsing it.

The Expat XML parser documentation contains the following security warning:

.. warning::

    The pyexpat module is not secure against maliciously constructed data. If you need to parse untrusted or unauthenticated data see :external+python:ref:`xml-vulnerabilities`.

USP minimally parses documents, so should avoid many of the risks seen in more complex parsers. Nevertheless, it is advisable to check the version of ``pyexpat`` against the notes listed in the mentioned section.

.. code-block:: python-console

    >>> import pyexpat
    >>> pyexpat.EXPAT_VERSION
    'expat_2.4.7'

Billion Laughs Attack
---------------------

To harden against the Billion Laughs attack, USP will not parse XML documents that contain a ``DOCTYPE`` or ``ENTITY`` declaration, which should never appear in a sitemap. 

Expat versions greater than 2.4.0 are resistent to most Billion Laughs attacks, although some variants are possible in versions below 2.7.2.