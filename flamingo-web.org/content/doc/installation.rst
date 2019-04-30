

Installation
============

The recommended way to install flamingo is using
`pip <https://pip.pypa.io/en/stable/>`_.

.. code-block::

    pip install flamingo

Flamingo supports `setuptools <https://setuptools.readthedocs.io/en/latest/>`_
optional features for having support for 3rd party libraries without defining
hard dependencies.

For example: If you want install flamingo with markdown support you have to
run pip like this.

.. code-block::

    pip install flamingo[markdown]

If you want to install **all** supported 3rd party libraries, run pip like
this:

.. code-block::

    pip install flamingo[full]


List of all optional features
-----------------------------

.. table::

    Name

    Description


    live-server

    Required for ``flamingo server``.
    Installs `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_,
    `aiohttp-json-rpc <https://github.com/pengutronix/aiohttp-json-rpc>`_,
    and `aionotify <https://github.com/rbarrois/aionotify>`_


    ipython

    Required for ``flamingo shell``. Installs `IPython <https://ipython.org/>`_


    chardet

    Adds support for
    `chardet <https://chardet.readthedocs.io/en/latest/index.html>`_.
    Needed for ``settings.USE_CHARDET``


    pygments

    Adds support for `pygments <http://pygments.org/>`_


    markdown

    Adds support for `markdown <https://www.markdownguide.org/>`_
    using `python-markdown <https://python-markdown.github.io/>`_


    coloredlogs

    Adds support for
    `coloredlogs <https://coloredlogs.readthedocs.io/en/latest/>`_
