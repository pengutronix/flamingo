def paginate(l, context):
    DEFAULT_PAGINATION = getattr(context.settings, 'DEFAULT_PAGINATION')
    l_count = len(l)

    if l_count > DEFAULT_PAGINATION:
        total_pages = (
            (l_count - (l_count % DEFAULT_PAGINATION)) // DEFAULT_PAGINATION
        ) + int((l_count % DEFAULT_PAGINATION) > 0)

    else:
        total_pages = 1

    for index in range(total_pages):
        yield (
            l[index*DEFAULT_PAGINATION:(index+1)*DEFAULT_PAGINATION],
            index + 1,
            total_pages,
        )
