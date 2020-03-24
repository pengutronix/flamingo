

Getting Started
===============

Installation
------------

First of all flamingo needs a proper python3.5+ environment.

.. code-block:: txt

    # apt install build-essential python3-dev python3-venv python3-pip


The recommended way to install flamingo is using
`pip <https://pip.pypa.io/en/stable/>`_.

.. code-block:: txt

    pip install flamingo


Start a new flamingo project
----------------------------

The simplest way to bootstrap a flamingo project is to use ``flamingo init``.
Flamingo does not enforce a specific project structure but comes with a number
of project templates.

A list of available project templates, their descriptions and variables is
available by running ``flamingo init -l``.

.. code-block:: text

    $ flamingo init wobsite project_name="Wobsite"
    $ cd wobsite/
    $ make html

The content of ``wobsite`` will look like this:

.. code-block:: text

    wobsite/
    ├── content/          # flamingo will search for content here recursively
    ├── Makefile
    ├── overlay/          # here you can place files like a robots.txt or a
    │                       favicon.ico
    ├── plugins/          # place your plugins here
    ├── README.rst
    ├── REQUIREMENTS.txt  # list of all python dependencies
    ├── settings.py       # all settings are stored here
    └── theme/            # root of all HTML templates, CSS- and JS files

The new project comes with a
`gnu make <https://www.gnu.org/software/make/>`_ file, that handles flamingo
dependencies in a python virtualenv, setting the right python version and holds
command line options for building.

To build the project run ``make html``.

Flamingo comes with a interactive webserver for writing content and debugging.
Run ``make server`` and go to ``localhost:8080`` with your
browser. Let server and browser run while writing your content. Flamingo
tracks file operations in ``content/``, rebuilds updated files and
refreshes the browser tab if needed.

Read more about {{ link('user/live_server.rst', 'flamingo Live-Server') }}.


Optional external dependencies
------------------------------

Flamingo supports `setuptools <https://setuptools.readthedocs.io/en/latest/>`_
optional features for having support for 3rd party libraries without defining
hard dependencies.

For example: If you want to install flamingo with markdown support you have to
change your ``REQUIREMENTS.txt`` like this:

.. code-block:: txt

    flamingo[live-server,markdown]

If you want to install **all** supported 3rd party libraries, run pip like
this:

.. code-block:: txt

    flamingo[full]


List of optional features
~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::

    ^Name ^Description
    |live-server |Required for flamingo server.  Installs aiohttp, aiohttp-json-rpc and IPython
    |ipython |Required for flamingo shell. Installs IPython
    |chardet |Adds support for chardet. Needed for settings.USE_CHARDET
    |pygments |Adds support for pygments
    |thumbnails |Adds support for image scaling. Installs pillow
    |markdown |Adds support for markdown using python-markdown
    |coloredlogs |Adds support for coloredlogs
