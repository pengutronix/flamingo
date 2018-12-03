def test_base_parser_import():
    from flamingo.core.parser import ContentParser  # NOQA


def test_meta_data_parsing():
    from io import StringIO

    from flamingo.core.parser import ContentParser
    from flamingo.core.data_model import Content

    raw_content = StringIO("""
    a: content of a
    b: content of b
    c:
        a, b, c


    content
    """)

    parser = ContentParser()
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'].strip() == 'a, b, c'

    assert content['content_body'] == 'content'

    # test with whitespaces
    raw_content = StringIO("""
    a: content of a
    b: content of b
    c:
        a, b, c
        

    content
    """)  # NOQA

    parser = ContentParser()
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'].strip() == 'a, b, c'

    assert content['content_body'] == 'content'
