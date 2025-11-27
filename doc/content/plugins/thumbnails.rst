

Thumbnails
==========

This plugin generates thumbnails of media contents. If a media content has
a ``width`` set, Thumbnails will create a thumbnail in ``THUMBNAIL_CACHE``, to
make it reusable, and will change the path of media content, so the new scaled
image get used for all later templates.

The original paths get stored in ``media_content['original']``.

Lets say you have a image named ``test.png``, which is 400px wide, and use it
in a content file like this:

.. code-block:: rst

    Hello world
    ===========

    .. image:: test.png
        :width: 200px

Thumbnails will create a file named ``test.thumb.png`` in
``setting.THUMBNAIL_CACHE`` and will override the path in the original media
content.


Installation
------------

Thumbnails depends of python-pillow, so flamingo has to be installed with
pillow support.

.. code-block:: txt

    # REQUIREMENTS.txt

    flamingo[thumbnails]

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Thumbnails',
    ]


Settings
--------

.. raw-setting::

    THUMBNAIL_CACHE = 'thumbs'

    Path of the directory where the thumbs get cached.
