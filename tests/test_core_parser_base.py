def test_base_parser_import():
    from flamingo.core.parser import ContentParser  # NOQA


def test_meta_data_parsing():
    from io import StringIO

    from flamingo.core.parser import ContentParser

    content = StringIO("""
    a: content of a
    b: content of b
    c:
        a, b, c


    content
    """)

    parser = ContentParser()
    meta_data, content = parser.parse(content)

    assert sorted(list(meta_data.keys())) == ['a', 'b', 'c']

    assert meta_data['a'] == 'content of a'
    assert meta_data['b'] == 'content of b'
    assert meta_data['c'].strip() == 'a, b, c'

    assert content == 'content'

    # test with whitespaces
    content = StringIO("""
    a: content of a
    b: content of b
    c:
        a, b, c
        

    content
    """)  # NOQA

    parser = ContentParser()
    meta_data, content = parser.parse(content)

    assert sorted(list(meta_data.keys())) == ['a', 'b', 'c']

    assert meta_data['a'] == 'content of a'
    assert meta_data['b'] == 'content of b'
    assert meta_data['c'].strip() == 'a, b, c'

    assert content == 'content'
