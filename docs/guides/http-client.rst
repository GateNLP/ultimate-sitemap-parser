HTTP Client
===========

By default, USP uses an HTTP client based on the `requests <https://docs.python-requests.org/en/master/>`_ library. This client can be passed options, a custom requests session, or can be replaced entirely with a custom client implementing the :class:`~usp.web_client.abstract_client.AbstractWebClient` interface.

Requests Client Options
-----------------------

To specify non-default options of the :class:`~usp.web_client.requests_client.RequestsWebClient`, manually instantiate it and pass it to the :func:`~usp.tree.sitemap_tree_for_homepage` function:

.. code-block:: python

    from usp.web_client.requests_client import RequestsWebClient
    from usp.tree import sitemap_tree_for_homepage

    client = RequestsWebClient(wait=5.0, random_wait=True)
    client.set_timeout(30)
    tree = sitemap_tree_for_homepage('https://www.example.org/', web_client=client)

See the constructor and methods of :class:`~usp.web_client.requests_client.RequestsWebClient` for available options.

Custom Requests Session
-----------------------

The default :external:py:class:`requests.Session` created by the client can be replaced with a custom session. This can be useful for setting headers, cookies, or other session-level options, or when replacing with a custom session implementation.

For example, to replace with the cache session provided by `requests-cache <https://requests-cache.readthedocs.io/en/latest/>`_:

.. code-block:: python

    from requests_cache import CachedSession
    from usp.web_client.requests_client import RequestsWebClient
    from usp.tree import sitemap_tree_for_homepage

    session = CachedSession('my_cache')
    client = RequestsWebClient(session=session)
    tree = sitemap_tree_for_homepage('https://www.example.org/', web_client=client)

Custom Client Implementation
----------------------------

To entirely replace the requests client, you will need to create subclasses of:

- :class:`~usp.web_client.abstract_client.AbstractWebClient`, implementing the abstract methods to perform the HTTP requests.
- :class:`~usp.web_client.abstract_client.AbstractWebClientSuccessResponse` to represent a successful response, implementing the abstract methods to obtain the response content and metadata.
- :class:`~usp.web_client.abstract_client.WebClientErrorResponse` to represent an error response, which typically will not require any methods to be implemented.

We suggest using the implementations in :mod:`usp.web_client.requests_client` as a reference.

After creating the custom client, instantiate it and pass to the ``web_client`` argument of :func:`~usp.tree.sitemap_tree_for_homepage`.

For example, to implement a client for the `HTTPX <https://www.python-httpx.org/>`_ library:

.. code-block:: python

    from usp.web_client.abstract_client import AbstractWebClient, AbstractWebClientSuccessResponse, WebClientErrorResponse

    class HttpxWebClientSuccessResponse(AbstractWebClientSuccessResponse):
        ...

    class HttpxWebClientErrorResponse(WebClientErrorResponse):
        pass

    class HttpxWebClient(AbstractWebClient):
        ...

    client = HttpxWebClient()
    tree = sitemap_tree_for_homepage('https://www.example.org/', web_client=client)
