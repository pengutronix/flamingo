def test_pagination(flamingo_dummy_context):
    from flamingo.core.utils.pagination import paginate

    # one page
    flamingo_dummy_context.settings.DEFAULT_PAGINATION = 10
    pages = list(paginate(list(range(0, 10)), flamingo_dummy_context))

    assert pages == [
        ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1, 1),
    ]

    # multiple pages
    flamingo_dummy_context.settings.DEFAULT_PAGINATION = 5
    pages = list(paginate(list(range(0, 10)), flamingo_dummy_context))

    assert pages == [
        ([0, 1, 2, 3, 4], 1, 2),
        ([5, 6, 7, 8, 9], 2, 2),
    ]
