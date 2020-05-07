

How to add a rst directive
==========================

When using reStructuredText, its often useful to add new directives.

`Official docutils directives documentation <https://docutils.sourceforge.io/docs/howto/rst-directives.html>`_


Simple directive
----------------

This example adds a simple directive that renders its content into a HTML pre
tag.

.. code-block:: python

    from docutils.parsers.rst import Directive
    from docutils.nodes import raw

    from flamingo.plugins.rst import register_directive


    class Pre(Directive):
        has_content = True

        def run(self):
            return [
                raw('', '<pre>{}</pre>'.format('\n'.join(self.content)),
                    format='html'),
            ]


    class rstPre:
        def parser_setup(self, context):
            register_directive('pre', Pre)


.. code-block:: rst

    .. pre::

        Lorem ipsum


.. code-block:: html

    <pre>Lorem ipsum</pre>


Directive with access to the context
------------------------------------

For some applications its needed to have access to the flamingo context and
its settings.

.. code-block:: python

    from docutils.parsers.rst import Directive
    from docutils.nodes import raw

    from flamingo.plugins.rst import register_directive


    def pre(context):
        class Pre(Directive):
            has_content = True

            def run(self):
                return [
                    raw('', '<pre>{}</pre>'.format('\n'.join(self.content)),
                        format='html'),
                ]

        return Pre


    class rstPre:
        def parser_setup(self, context):
            register_directive('pre', pre(context))


Directive that allows rst syntax
--------------------------------

Flamingos reStructuredText sub system supports inline rst syntax. This is
useful if you have more complex directives.

.. code-block:: python

    from docutils.nodes import raw

    from flamingo.plugins.rst import NestedDirective, register_directive


    def div(context):
        class Div(NestedDirective):
            def run(self):
                html = self.parse_content(context)

                return [
                    raw('', '<div>{}</div>'.format(html), format='html'),
                ]

        return Div


    class rstDiv:
        def parser_setup(self, context):
            register_directive('div', div(context))


.. code-block:: rst

    .. div::

        .. div::

            Hello World
            ===========


.. code-block:: html

    <div>
        <div>
            <h1>Hello World</h1>
        </div>
    </div>
