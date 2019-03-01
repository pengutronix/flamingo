def test_base_parser_import():
    from flamingo.core.parser import ContentParser  # NOQA


def test_basic_meta_data_parsing(dummy_context):
    from flamingo.core.parser import ContentParser
    from flamingo.core.data_model import Content

    raw_content = """
    a: content of a
    b: content of b
    c:
        a, b, c


    content
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'].strip() == 'a, b, c'

    assert content['content_body'] == 'content'

    # test with whitespaces
    raw_content = """
    a: content of a
    b: content of b
    c:
        a, b, c
        

    content
    """  # NOQA

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'].strip() == 'a, b, c'

    assert content['content_body'] == 'content'


def test_meta_data_blocks(dummy_context):
    from flamingo.core.parser import ContentParser
    from flamingo.core.data_model import Content

    # default block
    raw_content = """
    a: content of a
    b: content of b

    c: content of c


    content
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'] == 'content of c'
    assert content['content_body'] == 'content'

    # simple block
    raw_content = """
    a: content of a
    b: content of b
    c: content of c

    content
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'c', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['c'] == 'content of c'
    assert content['content_body'] == 'content'

    raw_content = """
    a: content of a
    b: content of b

    c: content of c

    real content
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert sorted(list(content.data.keys())) == ['a', 'b', 'content_body']

    assert content['a'] == 'content of a'
    assert content['b'] == 'content of b'
    assert content['content_body'].startswith('c: content of c\n')
    assert content['content_body'].endswith('real content')

    # no meta data
    raw_content = """
    real content1
    real content2
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert list(content.data.keys()) == ['content_body']
    assert content['content_body'].startswith('real content1')
    assert content['content_body'].endswith('real content2')

    raw_content = """
    real content1

    real content2
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert list(content.data.keys()) == ['content_body']
    assert content['content_body'].startswith('real content1')
    assert content['content_body'].endswith('real content2')

    raw_content = """
    real content1


    real content2
    """

    parser = ContentParser(dummy_context)
    content = Content()

    parser.parse(raw_content, content)

    assert list(content.data.keys()) == ['content_body']
    assert content['content_body'].startswith('real content1')
    assert content['content_body'].endswith('real content2')
