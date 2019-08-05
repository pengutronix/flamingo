import logging
import os

from aiohttp.web import FileResponse, Response

from flamingo.core.utils.aiohttp import no_cache


class ContentExporter:
    def __init__(self, context):
        self.context = context

        self.static_dirs = [
            os.path.dirname(i)
            for i in self.context.templating_engine.find_static_dirs()
        ]

        self.logger = logging.getLogger('flamingo.server.exporter')

    def resolve(self, request_path):
        # post build layers
        # static
        # media
        # content
        # pre build layers

        request_path = request_path[1:]

        if not request_path:
            request_path = 'index.html'

        self.logger.debug("request_path: '%s'", request_path)

        def _resolve_paths(paths):
            for path in paths[::-1]:
                path = os.path.join(path, request_path)

                if os.path.exists(path):
                    return path

            return ''

        # post build layers
        path = _resolve_paths(self.context.settings.POST_BUILD_LAYERS)

        if path:
            self.logger.debug("handled as post build layer: '%s'", path)

            return path

        # static files
        path = _resolve_paths(self.static_dirs)

        if path:
            self.logger.debug("handled as static file: '%s'", path)

            return path

        # media files
        media_link = '/' + request_path

        contents = self.context.contents.filter(
            media__passes=lambda m: m and m.filter(link=media_link).exists())

        if contents.exists():
            media_contents = contents.last()['media']
            media_content = media_contents.filter(link=media_link).last()

            self.context.run_plugin_hook('render_media_content', media_content)

            self.logger.debug("handled as media file: '%s'",
                              media_content['source'])

            return media_content['source']

        # content
        contents = self.context.contents.filter(output=request_path)
        content = None

        if contents.exists():
            content = contents.last()

        else:  # index.html
            contents = self.context.contents.filter(
                output=os.path.join(request_path, 'index.html')
            )

            if contents.exists():
                content = contents.last()

        if content:
            self.context.run_plugin_hook('render_content', content)

            self.logger.debug("handled as content: '%s'",
                              content['path'] or content)

            return content

        # pre build layers
        path = _resolve_paths(self.context.settings.PRE_BUILD_LAYERS)

        if path:
            self.logger.debug("handled as pre build layer: '%s'", path)

            return path

    @no_cache()
    async def __call__(self, request):
        def gen_response(content):
            # 404
            if not content:
                self.logger.debug('404: not found')

                return Response(text='404: not found', status=404)

            # file response
            if isinstance(content, str):
                return FileResponse(content)

            # content response
            output = self.context.render(content)

            return Response(text=output, content_type='text/html')

        try:
            response = gen_response(self.resolve(request.path))

        except Exception as e:
            self.context.logger.error(e, exc_info=True)

        return response
