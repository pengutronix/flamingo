

Writing plugins
===============

All flamingo plugins have to be a python class, defining hooks which are simple
python methods.

All hooks get the ``context`` object passed in. Some hooks get
``flamingo.Content`` objects passed in. More information on Content objects:
{{ link('developer/data_model.rst', 'Flamingo data model') }}


.. code-block:: python

    class ExamplePlugin:
        # The name of your plugin is irrelevant to flamingo. You can name it
        # how you want

        def setup(self, context):
            # Gets called on plugin setup and is meant to setup plugin
            # specific state.
            # When the Live-Server is running this hook gets re executed
            # every time a rebuild is triggered.

            pass

        def settings_setup(self, context):
            # Gets called when all settings are setup.
            # You can change global settings here.

            pass

        def parser_setup(self, context):
            # Gets called after all parsers are setup.
            # Use this hook to register rst directives.

            pass

        def templating_engine_setup(self, context, templating_engine):
            # Gets called when the templating engine is ready.
            # Use this hook to register your Jinja2 filters.

            pass

        def media_added(self, context, content, media_content):
            # Gets called every time a new media content gets added using
            # context.add_media().
            # You can use this hook to change meta data on media contents or
            # scale images for example.
            # 'media_content' contains the media content that got added,
            # 'content' the related content object.

            pass

        def content_parsed(self, context, content):
            # Gets called every time a content file gets parsed.
            # The current content is available in context.content.

            pass

        def contents_parsed(self, context):
            # Gets called when all content files in CONTENT_ROOT are parsed.
            # All content objects are available in context.contents.

            pass

        def context_setup(self, context):
            # Gets called when the context is set up fully.

            pass

        def pre_build(self, context):
            # Gets called as last hook before building.

            pass

        def template_context_setup(self, content, template_name,
                                   template_context):

            # Gets called while rendering a content object. When rendering a
            # content object a template context gets created. You can use this
            # hook to change or extend templating contexts

            pass

        def post_build(self, context):
            # Gets called after building.

            pass

        # Live-Server specific hooks
        # these hook only run if the Live-Server runs and are meant to be used
        # to increase performance by rendering only contents that have been
        # requested

        def render_content(self, context, content):
            # This hook gets called for every Content object that gets rendered
            # by the Live-Server.

            pass

        def render_media_content(self, context, media_content):
            # This hook gets called for every media Content object that gets
            # rendered by the Live-Server.

            pass

Flamingo plugins can be loaded from python packages or directly from files.
They don't have to be importable or setuptools packaged.

.. code-block:: python

    # plugins/example_plugin.py

    class ExamplePlugin:
        def contents_parsed(self, context):
            print(context.contents)


    # settings.py

    Plugins = [
        'plugins/example_plugin.py::ExamplePlugin',
    ]


Error reporting
---------------

pythons logging module is highly integrated into flamingo and especially into
flamingo Live-Server.

See {{ link('user/live_server.rst', 'Live-Server') }} documentation for more
details.


Define your own hooks
---------------------

Besides the default hooks, you can define your own hooks by simply running
them.

.. code-block:: python

	context.plugins.run_hook('my_special_hook')

This can be useful if you want to write a complex parser with intermediate
states. The reStructuredText parser, for instance, produces a docutils document
tree before generating HTML.

.. code-block:: python

	# flamingo/plugins/rst/base.py

	# [...]
	context.plugins.run_hook('rst_document_parsed', document)
	# [...]


Plugins with state
------------------

For some applications plugins need state. The reStructuredText plugin for
example needs to hold state of the current parsed line for correct error
reporting.

To setup your plugins state you can use the hook ``setup()``. It gets executed
once on setup and every time a rebuild is triggered, if the Live-Server is 
running.

If you need to access the state of another plugin you can get it by using
``context.plugins.get_plugin(class_name)``.

.. code-block:: python

    class ExamplePlugin:
        def setup(self, context):
            self.internal_counter = 0

        def content_parsed(self, context, content):
            self.internal_counter += 1


    class ExamplePlugin2:
        def content_parsed(self, context, content):
            example_plugin = context.plugins.get_plugin('ExamplePlugin')
            example_plugin.internal_counter += 1


Media
-----

Flamingo uses the same data model for media objects like for
{{ link('developer/data_model.rst', 'content objects') }}. When a media content
gets added to a content object, it get stored in ``content['media']``.

Lets say you want to create a plugin that adds an image with the same name
as the content it is placed next to.

The ``context`` class defines ``add_media()`` for this manner. It takes a name,
which has to be a path in file system, within your ``settings.CONTENT_ROOT``
and a ``Content`` object (media is always related to content, not to your
project).

If ``name`` starts with an ``/``, the path is considered an absolute path,
relative to your ``settings.CONTENT_ROOT``. If it doesn't, it has be relative
to your ``content['path']``.

You also can add your own custom meta data.


.. code-block:: python

    import os

    class ExamplePlugin:
        def content_parsed(self, context, content):
            new_media_content = context.add_media(
                name='image.jpg',
                content=content,
                
                # some custom meta data
                foo='bar',
            )

        def media_added(self, context, content, media_content):
            if media_content['foo']:
                print(media_content)


Themes
------

If your plugin comes with templates or static files, your plugin can also be a
theme.

A theme contains two directories: ``templates`` and ``static``.

For example the directory structure of the ``Tags`` plugin looks like this:

.. code-block:: txt

    tags/
    ├── __init__.py
    ├── tags.py
    └── theme
        └── templates
            ├── tag.html
            └── tags.html

To tell flamingo where to search for a theme ``THEME_PATHS`` is used:

.. code-block:: python

	import os


	class Tags:
		THEME_PATHS = [os.path.join(os.path.dirname(__file__), 'theme')]


Live-Server aware plugins
-------------------------

Lets say you have a plugin that generates thumbnails of large images.

.. code-block:: python

    class Thumbnails:
        def media_added(self, context, content, media_content):
            generate_thumbnail(media_content['path'], 'image.thumb.jpg')


For plain rendering your project with ``make html`` this is totally fine, but
when running the Live-Server, this will slow down your the startup of
``make server`` by every new image you add.

Flamingo has special hooks to address this.

.. code-block:: python

    class Thumbnails:
        def media_added(self, context, content, media_content):
            thumbnail = context.add_media(
                name='image.thumb.jpg',
                content=content,

                # we use this meta data as hint for later
                thumbnail=True,
            )

            # The Live-Server sets this variable on startup
            if context.settings.LIVE_SERVER_RUNNING:
                return

            generate_thumbnail(thumbnail['path'], 'image.thumb.jpg')

        def render_media_content(self, context, media_content):
            # the meta data we added before
            if media_content['thumbnail'] == True:
                if not os.path.exists(media_content['path']):

                    generate_thumbnail(media_content['path'],
                                       'image.thumb.jpg')
