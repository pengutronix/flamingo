def test_rst_parsing(flamingo_dummy_context):
    from flamingo.plugins.rst.base import RSTParser
    from flamingo.core.data_model import Content

    raw_content = """
title: foo


bar
===

foobar"""

    parser = RSTParser(flamingo_dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert content['title'] == 'foo'
    assert content['content_title'] == 'bar'
    assert content['content_body'] == '<p>foobar</p>\n'


def test_error_line_number():
    import pytest

    from flamingo.plugins.rst.base import (
        reStructuredTextError,
        parse_rst_parts,
    )

    # one liner
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts('.. foo::')

    assert exc_info.value.line == 1

    # multi line with heading
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts("""Foo
===


.. foo::""")

    assert exc_info.value.line == 5

    # multi line without heading
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts("""



.. foo::""")

    assert exc_info.value.line == 5


def test_parsing_error_while_building(flamingo_env):
    from flamingo.plugins.rst.base import reStructuredTextError

    flamingo_env.write('/content/a.rst', """
    a: 1
    b: 2

    .. foo::
    """)

    flamingo_env.build()

    assert len(flamingo_env.context.errors) == 1
    assert isinstance(flamingo_env.context.errors[0], reStructuredTextError)

    assert ('Unknown directive type "foo"' in
            flamingo_env.context.errors[0].short_description)


def test_error_while_parsing_error():
    import pytest

    from flamingo.plugins.rst.base import parse_rst_parts
    from docutils.utils import SystemMessage

    with pytest.raises(SystemMessage) as exc_info:
        parse_rst_parts('.. foo::', system_message_re=None)

    assert 'Unknown directive type "foo"' in exc_info.value.args[0]
