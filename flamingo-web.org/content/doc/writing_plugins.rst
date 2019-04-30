

Writing plugins
===============

A flamingo plugin consists only of hooks.

.. code-block:: python

    class ExamplePlugin:
        def parser_setup(self, context):
            # gets called after all parsers are setup
            # use this hook to register rst directives

            pass

        def content_parsed(self, context, content):
            # gets called every time a content file gets parsed
            # the current content is available in context.content

            pass

        def contents_parsed(self, context):
            # gets called when all content files in CONTENT_ROOT are parsed
            # all content objects are available in context.contents

            pass

        def templating_engine_setup(self, context, templating_engine):
            # gets called when the templating engine is ready
            # use this hook to register your Jinja2 filters

            pass

        def context_setup(self, context):
            # gets called when the context is set up fully

            pass

        def pre_build(self, context):
            # gets called as last hook before building

            pass

        def post_build(self, context):
            # gets called after building

            pass

Flamingo plugins can be loaded from packages or directly from files. They don't
have to be importable.

.. code-block:: python

    # plugins/test.py

    class ExamplePlugin:
        def contents_parsed(self, context):
            print(context.contents)


    # settings.py

    Plugins = [
        'flamingo.plugins.Tags',
        'plugins/test.py::ExamplePlugin',
    ]


Hooks
-----

Sometimes a plugin is a little bit much for a simple approach. Lets say you
want to delete all Contents from output that have a specific path prefix.

.. code-block:: python

    # settings.py

    import flamingo

    @flamingo.hook('contents_parsed')
    def remove_contents(context):
        context.contents = context.contents.exclude(path__starstwith='foo/')
