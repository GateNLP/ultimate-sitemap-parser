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

It is recommended to use a version greater than 2.4.0, which should be included in all recent Python versions.