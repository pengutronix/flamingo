from functools import wraps


def no_cache():
    def wrapper(coroutine):
        @wraps(coroutine)
        async def wrapped(*args):
            response = await coroutine(*args)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # NOQA

            return response

        return wrapped

    return wrapper
