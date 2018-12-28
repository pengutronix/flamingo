def test_basic_queries():
    from flamingo.core.data_model import Content, Q

    c = Content(a=10, b=20)

    assert Q(a=10).check(c)
    assert not Q(a=20).check(c)
    assert Q(Q(Q(Q(Q(a=10))))).check(Content(a=10))


def test_and():
    from flamingo.core.data_model import Content, Q

    c = Content(a=10, b=20)

    assert (Q(a=10) & Q(b=20)).check(c)
    assert not (Q(a=10) & Q(b=21)).check(c)


def test_or():
    from flamingo.core.data_model import Content, Q

    q = Q(a=10) | Q(b=10)

    assert q.check(Content(a=10, b=20))
    assert q.check(Content(a=20, b=10))

    assert not q.check(Content(b=20))
    assert not q.check(Content(a=20))


def test_not():
    from flamingo.core.data_model import Content, Q

    q = ~Q(a=1)

    assert q.check(Content(a=2))
    assert not q.check(Content(a=1))


def test_f():
    from flamingo.core.data_model import Content, Q, F

    q = Q(a=F('b'))

    assert q.check(Content(a=1, b=1))
    assert not q.check(Content(a=1, b=2))


def test_filter():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a=5)

    assert cs.count() == 1
    assert cs[0]['a'] == 5


def test_add():
    from flamingo.core.data_model import ContentSet, Content

    cs = ContentSet()
    c1 = Content(a=1)
    c2 = Content(a=2)

    cs.add(c1)

    assert c1 in cs
    assert c2 not in cs

    cs = cs + c2

    assert c1 in cs
    assert c2 in cs


def test_iadd():
    from flamingo.core.data_model import ContentSet, Content

    cs = ContentSet()
    c1 = Content(a=1)
    c2 = Content(a=2)

    cs.add(c1)

    assert c1 in cs
    assert c2 not in cs

    cs += c2

    assert c1 in cs
    assert c2 in cs


def test_sub():
    from flamingo.core.data_model import ContentSet, Content

    cs = ContentSet()
    c1 = Content(a=1)
    c2 = Content(a=2)

    cs.add(c1)
    cs.add(c2)

    assert c1 in cs
    assert c2 in cs

    cs = cs - c2

    assert c1 in cs
    assert c2 not in cs


def test_isub():
    from flamingo.core.data_model import ContentSet, Content

    cs = ContentSet()
    c1 = Content(a=1)
    c2 = Content(a=2)

    cs.add(c1)
    cs.add(c2)

    assert c1 in cs
    assert c2 in cs

    cs -= c2

    assert c1 in cs
    assert c2 not in cs
