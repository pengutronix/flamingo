is_template: False


Writing Content
===============

**Note:** The syntax for features like HTML links or images may vary between
different input formats.

Content files consists of two sections: Meta data and content. The meta data
get parsed by `YAML <https://pyyaml.org/wiki/PyYAMLDocumentation>`_, the
content according to the file extension.

The meta data block comes first and is divided from the content block by two
or more blank lines. If you won't set any meta data your content file has to
start with two or more blank lines.

.. code-block:: rest

    # content/hello-world.rst
    title: hello-world
    a: foo
    b: bar


    Hello World!
    ============

    Lorem Ipsum

The parsed ``flamingo.Content`` object will look like this:

.. code-block:: python

    In [1]: content['title']
    Out[1]: 'hello-world'

    In [2]: content['a']
    Out[2]: 'foo'

    In [3]: content['content_title']
    Out[3]: 'Hello World!'

    In [4]: content['content_body']
    Out[4]: '<p>Lorem Ipsum</p>'


Special Attributes
------------------

.. table::

    ^Name ^Description
    |path |Contains the path to this content, relative to the CONTENT_ROOT. This attribute is set by flamingo and is not meant to be set in a content file.
    |output |Contains the output path of this content. If not set it gets auto generated from its path.  When the path is foo/bar/bar.rst the output would be foo/bar/bar.html
    |url |a linkable url to this content
    |title |content of the HTML title tag when rendering
    |template |template name that gets used to render the content. Default is page.html. You can change this to your own template name
    |content_title |all parsers split the content in its first heading and all following content. content_title holds the first heading of the content
    |content_body |all parsers split the content in its first heading and all following content. content_body holds the all content but the first heading
    |media |a flamingo.core.data_model.ContentSet that holds all paths of media files used in this content


Using Jinja2 Syntax
-------------------

When ``settings.PRE_RENDER_CONTENT`` is enabled, every content file can be a
template:

.. code-block:: jinja

    # content/test.html
    title: test


    <h1>List of all Contents with the tag "foo"</h1>

    <ul>
        {% for content in context.contents.filter(tags__contains='foo') %}
            <a href="{{ content.url }}">{{ content.title }}</a>
        {% endfor %}
    </ul>


Generating links
````````````````

.. code-block:: rst

    # content/link.rst
    title: link


    Link to "Test document"
    =======================

    {{ link('content/test.rst', 'Test document') }}
