

Redirects
=========

This plugin adds a parser for redirect rule files. Redirects get created as
a HTML page with a refresh header set. Because of this currently only ``302``
redirects are supported.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Redirects',
    ]


Usage
-----

.. code-block:: txt

    # content/historic_link.rr

    302 /old_link_format.html   /new/link/format.html
