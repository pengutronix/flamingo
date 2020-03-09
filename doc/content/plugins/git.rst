is_template: false


Git
===

This plugin is used to add a git version string to your template contexts.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Git',
    ]


Settings
--------

.. raw-setting::

    GIT_VERSION_CMD = 'git describe'

.. raw-setting::

    GIT_VERSION_EXTRA_CONTEXT_NAME = 'GIT_VERSION'


Usage
-----

.. code-block:: html

    <!-- base.html -->

    <h1>Flamigo documentation<small>{{ GIT_VERSION }}</small></h1>
