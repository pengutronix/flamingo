

Layers
======

Layers are meant for all kind of non-content, static files that are very
project specific, or have to be at a very specific location in the build
output, for example a favicon or a Google analytics file.

A layer is just a plain directory within your project, but outside of your
content root. If you place a file ``foo/bar/baz.txt`` in a layer, it will be
copied to ``output/foo/bar/baz.txt``. Layers can override each over and get
handled top-down.

Layers can be part of a soft migration strategy from another framework. 
Let's say you have an existing pelican project you want to slowly migrate from.
Put pelicans output to a directory for example named ``attic`` and add
``attic`` to ``PRE_BUILD_LAYERS``. Flamingo will copy your old files to its own
output directory before building and you can support your old and new contents
at the same time.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Layers',
    ]


Usage
-----

.. code-block:: python

    # settings.py

    PRE_BUILD_LAYERS = [
        'attic',
        'attic2',
    ]

    POST_BUILD_LAYERS = [
        'overlay',
    ],
