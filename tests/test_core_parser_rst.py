def test_rst_parsing(flamingo_dummy_context):
    import re

    from flamingo import Content
    from flamingo.plugins.rst.plugin import RSTParser

    raw_content = """
title: foo


bar
===

foobar"""

    parser = RSTParser(flamingo_dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    content_body = re.sub(r"\s+", "", content["content_body"])

    assert content["title"] == "foo"
    assert content["content_title"] == "bar"
    assert content_body == '<divclass="section"id="bar">foobar</div>'


def test_error_line_number(flamingo_dummy_context):
    import pytest

    from flamingo.plugins.rst import (
        parse_rst_parts,
        reStructuredTextError,
    )

    # one liner
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts(".. foo::", flamingo_dummy_context)

    assert exc_info.value.line == 1

    # multi line with heading
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts(
            """Foo
===


.. foo::""",
            flamingo_dummy_context,
        )

    assert exc_info.value.line == 5

    # multi line without heading
    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts(
            """



.. foo::""",
            flamingo_dummy_context,
        )

    assert exc_info.value.line == 5


def test_parsing_error_while_building(flamingo_env):
    from flamingo.plugins.rst import reStructuredTextError

    flamingo_env.write(
        "/content/a.rst",
        """
    a: 1
    b: 2


    .. foo::
    """,
    )

    flamingo_env.build()

    assert len(flamingo_env.context.errors) == 1
    assert isinstance(flamingo_env.context.errors[0], reStructuredTextError)

    assert 'Unknown directive type "foo"' in flamingo_env.context.errors[0].short_description


def test_error_while_parsing_error(flamingo_dummy_context):
    import pytest

    from flamingo.plugins.rst import (
        parse_rst_parts,
        reStructuredTextError,
    )

    with pytest.raises(reStructuredTextError) as exc_info:
        parse_rst_parts(".. foo::", flamingo_dummy_context, system_message_re=None)

    assert 'Unknown directive type "foo"' in exc_info.value.short_description


def test_includes(flamingo_env):
    flamingo_env.write(
        "/content/a.rst",
        """


    AAA
    ===

    .. include:: /c.rst
        :title: Foo Bar

    """,
    )

    flamingo_env.write(
        "/content/b.rst",
        """


    BBB
    ===

    no content

    """,
    )

    flamingo_env.write(
        "/content/c.rst",
        """


    CCC
    ===

    .. include:: /d.rst
        :title: Foo Bar

    """,
    )

    flamingo_env.write(
        "/content/d.rst",
        """


    DDD
    ===

    Foo Bar
    -------

    actual content

    """,
    )

    # the CONTENT_PATHS get set by hand to enforce the right order
    flamingo_env.settings.CONTENT_PATHS = ["a.rst", "b.rst", "c.rst", "d.rst"]

    flamingo_env.build()

    assert "actual content" in flamingo_env.read("/output/a.html")
