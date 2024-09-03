Saving
======

USP supports two methods of serialisation: conversion to a dictionary or Pickle format.

As Dictionary
-------------

Trees and pages can be converted into a dictionary with the :meth:`AbstractSitemap.to_dict() <usp.objects.sitemap.AbstractSitemap.to_dict>`/:meth:`SitemapPage.to_dict() <usp.objects.page.SitemapPage.to_dict>` methods.

For example:

.. code-block:: py

    tree = sitemap_tree_for_homepage('https://www.example.org/')

    # Complete tree representation with pages
    tree.to_dict()

    # Tree representation without pages
    tree.to_dict(include_pages=False)

    # Pages only
    [page.to_dict() for page in tree.all_pages()]

This could then be used with another library for data manipulation, such as Pandas:

.. code-block:: py

    data = [page.to_dict() for page in tree.all_pages()]
    # pd.json_normalize() flattens the nested key for news stories
    # to dot-separated keys
    pages_df = pd.DataFrame(pd.json_normalize(data))

    pages_df.to_csv('sitemap-pages.csv', index=False)


As Pickle
---------

If you need to save the tree object itself in a format which can be loaded back later, use the :external+python:doc:`Pickle format<library/pickle>`. The :class:`~usp.objects.sitemap.AbstractPagesSitemap` class implements custom pickling behaviour to load pages from disk, and unpickling behaviour to save them back.

.. danger::

    Loading Pickle data from untrusted sources can be unsafe. See the :external+python:doc:`pickle module documentation <library/pickle>`

.. danger::

    Pickling and unpickling relies on the internal private API of USP **which may change in future versions, even if the public API remains the same**. Attempting to load a pickled tree from a different version of USP may result in errors or incorrect data.

.. warning::

    All pages will need to be loaded into memory to pickle/unpickle the tree, so be cautious with very large sitemaps.


.. code-block:: py

    import pickle
    from usp.tree import sitemap_tree_for_homepage

    tree = sitemap_tree_for_homepage('https://www.example.org/')

    with open('sitemap.pickle', 'wb') as f:
        pickle.dump(tree, f)

    # This will delete the temporary files used to store the pages of the tree
    del tree

    # Later, to load the tree back

    with open('sitemap.pickle', 'rb') as f:
        tree = pickle.load(f)

    for page in tree.all_pages():
        print(page.url)
