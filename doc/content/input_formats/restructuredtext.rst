is_template: False


reStructuredText
================

The plugin ``flamingo.plugins.reStructuredText`` adds support for
reStructuredText using `docutils <https://docutils.sourceforge.io/>`__.

.. code-block:: rst

    title: hello world


    Hello World!
    ============

    Lorem ipsum


Settings
--------

.. raw-setting::

    RST_SETTINGS_OVERRIDES = {}

    The parser sets some defaults in the reStructuredText parser settings.
    You can override them here. List of all settings:
    [`link <https://docutils.sourceforge.io/docs/user/config.html>`__]

.. setting::
    :name: DEFAULT_IMAGE_TEMPLATE
    :path: flamingo.core.settings.defaults.DEFAULT_IMAGE_TEMPLATE

.. setting::
    :name: DEFAULT_GALLERY_TEMPLATE
    :path: flamingo.core.settings.defaults.DEFAULT_GALLERY_TEMPLATE

.. raw-setting::

    RST_IMAGE_EXTRA_OPTION_SPEC = {}

.. raw-setting::

    RST_GALLERY_EXTRA_OPTION_SPEC = {}

.. raw-setting::

    RST_IMAGE_DIRECTIVE_NAMES = ['img', 'image']

.. raw-setting::

    RST_GALLERY_DIRECTIVE_NAMES = ['gallery']

.. raw-setting::

    RST_IMAGE_CAPTION_RAW = False

    When set to ``True`` no inline rst is allowed in image captions

.. raw-setting::

    RST_REMOVE_SYSTEM_MESSAGES_FROM_OUPUT = True

    By default reStructuredText adds system messages to the HTML output


Links
-----

The reStructuredText subsystem uses a text role named ``:link:`` for internal
and external links.

Link support gets handled by ``flamingo.plugins.rstLink``.


External links
~~~~~~~~~~~~~~

Flamingo determines if a link is external by checking if the link target
defines a protocol like ``http://``, ``ftp://`` or ``mailto:``.

If no link title is given, the target is used as title.

.. code-block:: rst

    Link with title
    ===============

    :link:`Flamingo documentation <http://flamingo.org>`


    Link without Title
    ==================

    :link:`http://flamingo.org`


Internal links, downloads
~~~~~~~~~~~~~~~~~~~~~~~~~

Internal links always have to point to real paths in ``settings.CONTENT_ROOT``.
Paths are always relative to the current file, except if the path starts with
``/``. In this case it has to be a absolute path.

Link targets can be downloadable files.


.. code-block:: rst

    Link with title
    ===============

    :link:`home.rst`


    Link without Title
    ==================

    :link:`Link to home <home.rst>`


Images
------

Images get handled by a directive. All extra options can be left out.
The first argument of the directive has to be the path to your image. If the
path starts with a ``/``, the path has to be absolute to the ``CONTENT_ROOT``,
if not, relative to the content file, the image is used in.

Image support gets handled by ``flamingo.plugins.rstImage``.

.. code-block:: rst

    .. image:: foo.png

    .. image:: bar.png
        :template: 'image.html'  # if not set DEFAULT_IMAGE_TEMPLATE gets used
        :align: left  # possible values: 'left', 'center', 'right'
        :clear: both
        :width: 200px
        :height: 200px
        :link: www.example.org
        :alt: My bar image
        :title: My bar image

        This is the caption of my bar image.


Extending the image directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need more options, you don't have to create a new image directive, you
can extend the existing one.

.. code-block:: python

    # settings.py
    from docutils.parsers.rst import directives

    RST_IMAGE_EXTRA_OPTION_SPEC = {
        'licence': directives.unchanged,
    }


.. code-block:: rst

    .. image:: foo.png
        :license: Apache2
        :template: licensed_image.html


.. code-block:: html

    <!-- theme/templates/licensed_image.html -->
    <img src="{{ content.url }}">
    <p>This image is licensed under {{ content.license }}</p>


Galleries
~~~~~~~~~

Galleries are used to group images together.

.. code-block:: rst

    .. gallery::

        .. image:: image1.png

            This is the first image of this gallery.

        .. image:: image1.png

            This is the second.


Code blocks
-----------

Code blocks are add support for `pygments <https://pygments.org/>`__.
To use code blocks flamingo has to be installed with pygments support.

.. code-block:: txt

    # REQUIREMENTS.txt

    flamingo[pygments]

.. code-block:: rst

    .. code-block:: python

        for i in range(10):
            print(i)
