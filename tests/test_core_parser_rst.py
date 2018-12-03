def test_rst_parsing():
    from io import StringIO

    from flamingo.core.plugins.rst.base import RSTParser
    from flamingo.core.data_model import Content

    raw_content = StringIO("""
title: foo


bar
===

foobar""")

    parser = RSTParser()
    content = Content()

    parser.parse(raw_content, content)

    assert content['title'] == 'foo'
    assert content['content_title'] == 'bar'
    assert content['content_body'] == '<p>foobar</p>\n'
