import os

from aiohttp.web import StaticResource


class Exporter:
    def __init__(self, path, prefix=''):
        self.path = path
        self.prefix = prefix
        self.resource = StaticResource('', path, show_index=True)
        self.show_index = False

    async def __call__(self, request):
        path = request.path

        # remove prefix
        if self.prefix:
            path = os.path.join('/',
                                os.path.relpath(request.path, self.prefix))

        # directory listing / serving index
        if not self.show_index:
            test_path = path

            if test_path.startswith('/'):
                test_path = test_path[1:]

            test_path = os.path.join(self.path, test_path)

            if os.path.isdir(test_path):
                test_path = os.path.join(test_path, 'index.html')

                if os.path.exists(test_path):
                    path = os.path.join(path, 'index.html')

        # run static resource
        request.match_info['filename'] = path[1:]
        response = await self.resource._handle(request)

        # disable caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # NOQA

        return response
