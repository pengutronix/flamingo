def test_rst_parsing(dummy_context):
    from flamingo.plugins.rst.base import RSTParser
    from flamingo.core.data_model import Content

    raw_content = """
title: foo


bar
===

foobar"""

    parser = RSTParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert content['title'] == 'foo'
    assert content['content_title'] == 'bar'
    assert content['content_body'] == '<p>foobar</p>\n'
