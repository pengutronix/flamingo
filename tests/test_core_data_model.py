import pytest


def test_q_api():
    from flamingo.core.data_model import Content, Q

    # to few arguments
    with pytest.raises(TypeError) as excinfo:
        Q()

    assert str(excinfo.value) == "to few arguments"

    # to many arguments
    with pytest.raises(TypeError) as excinfo:
        Q(Q(a=1), b=2)

    assert str(excinfo.value) == "to many arguments"

    c = Content(a=10, b=20)

    assert Q(a=10).check(c)
    assert Q({"a": 10}).check(c)
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

    q = Q(a=F("b"))

    assert q.check(Content(a=1, b=1))
    assert not q.check(Content(a=1, b=2))


def test_filter():
    from flamingo.core.data_model import ContentSet

    # keyword args
    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a=5)

    assert cs.count() == 1
    assert cs[0]["a"] == 5

    # dict
    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter({"a": 5})

    assert cs.count() == 1
    assert cs[0]["a"] == 5


def test_exclude():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.exclude(a=5)

    assert [i["a"] for i in cs] == [0, 1, 2, 3, 4, 6, 7, 8, 9]


def test_ne():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__ne=5)

    assert [i["a"] for i in cs] == [0, 1, 2, 3, 4, 6, 7, 8, 9]


def test_lt():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__lt=5)

    assert [i["a"] for i in cs] == [0, 1, 2, 3, 4]


def test_lte():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__lte=5)

    assert [i["a"] for i in cs] == [0, 1, 2, 3, 4, 5]


def test_gt():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__gt=5)

    assert [i["a"] for i in cs] == [6, 7, 8, 9]


def test_gte():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__gte=5)

    assert [i["a"] for i in cs] == [5, 6, 7, 8, 9]


def test_in():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i)

    cs = cs.filter(a__in=[4, 5, 8])

    assert [i["a"] for i in cs] == [4, 5, 8]


def test_ContentSet_get():
    from flamingo.core.data_model import ContentSet

    from flamingo.core.errors import (
        MultipleObjectsReturned,
        ObjectDoesNotExist,
    )

    # single object
    cs = ContentSet()

    cs.add(a=1)

    assert cs.get()["a"] == 1

    # simple get
    cs = ContentSet()

    cs.add(a=1)
    cs.add(a=2)

    assert cs.get(a=1)["a"] == 1

    # MultipleObjectsReturned
    cs = ContentSet()

    cs.add(a=1)
    cs.add(a=1)

    with pytest.raises(MultipleObjectsReturned):
        assert cs.get()

    with pytest.raises(MultipleObjectsReturned):
        assert cs.get(a=1)

    # ObjectDoesNotExist
    cs = ContentSet()

    cs.add(a=1)
    cs.add(a=2)

    with pytest.raises(ObjectDoesNotExist):
        assert cs.get(a=3)


def test_Content_get():
    from flamingo.core.data_model import Content

    c = Content(a=1)

    assert c.get("a") == 1
    assert not c.get("b")
    assert c.get("b", 2) == 2


def test_values():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    for i in range(10):
        cs.add(a=i, b=i + 1, c=i if i % 2 == 0 else None)

    assert cs.values("a", "b", "c") == [
        (0, 1, 0),
        (1, 2, None),
        (2, 3, 2),
        (3, 4, None),
        (4, 5, 4),
        (5, 6, None),
        (6, 7, 6),
        (7, 8, None),
        (8, 9, 8),
        (9, 10, None),
    ]

    assert cs.values("c") == [0, 2, 4, 6, 8]


def test_order_by():
    from flamingo.core.data_model import ContentSet

    cs = ContentSet()

    cs.add(a=4)
    cs.add(a=3)
    cs.add(a=5)
    cs.add(a=1)
    cs.add(a=2)

    assert [i["a"] for i in cs] == [4, 3, 5, 1, 2]
    assert [i["a"] for i in cs.order_by("a")] == [1, 2, 3, 4, 5]
    assert [i["a"] for i in cs.order_by("-a")] == [5, 4, 3, 2, 1]


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


def test_copy():
    from flamingo.core.data_model import ContentSet
    from copy import deepcopy

    cs1 = ContentSet()
    cs1.add(a=1)
    cs2 = deepcopy(cs1)

    assert cs1[0]["a"] == cs2[0]["a"]
    assert cs1[0] is not cs2[0]
