def paginate(objects, context):
    """
    yields: page, page_index, total_pages

    """

    DEFAULT_PAGINATION = getattr(context.settings, 'DEFAULT_PAGINATION')
    object_count = len(objects)

    if object_count > DEFAULT_PAGINATION:
        total_pages = (
            (object_count - (object_count %
                             DEFAULT_PAGINATION)) // DEFAULT_PAGINATION
        ) + int((object_count % DEFAULT_PAGINATION) > 0)

    else:
        total_pages = 1

    for index in range(total_pages):
        yield (
            objects[index*DEFAULT_PAGINATION:(index+1)*DEFAULT_PAGINATION],
            index + 1,
            total_pages,
        )
