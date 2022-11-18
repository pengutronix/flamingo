from concurrent.futures import CancelledError
import logging
import os

from aiohttp.web import FileResponse, HTTPFound, Response
from jinja2 import Template

from flamingo.core.data_model import ContentSet, Content
from flamingo.core.utils.pprint import pformat


TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), 'templates')
DIRECTORY_LIST_HTML = os.path.join(TEMPLATE_ROOT, 'directory_list.html')


class History:
    def __init__(self):
        self.clear()

    def clear(self):
        self.history = []
        self.contents = ContentSet()

    def append(self, item):
        self.history.append(item)

        if isinstance(item, Content):
            self.contents.add(item)

    def __iter__(self):
        return self.history.__iter__()

    def __repr__(self):
        return pformat(self.history)


class ContentExporter:
    def __init__(self, server):
        self.server = server

        self.logger = logging.getLogger('flamingo.server.exporter')

    @property
    def context(self):
        return self.server.build_environment.context

    @property
    def history(self):
        return self.server.history

    @property
    def static_dirs(self):
        return [
            os.path.dirname(i)
            for i in self.server.context.templating_engine.find_static_dirs()
        ]

    @property
    def directory_index(self):
        return self.server.options['directory_index']

    @property
    def directory_listing(self):
        return self.server.options['directory_listing']

    def clear(self):
        self.logger.debug('clearing history...')
        self.history.clear()

    def resolve(self, request_path):
        # post build layers
        # static
        # media
        # content
        # pre build layers

        request_path = request_path[1:]

        if not request_path and self.directory_index:
            request_path = 'index.html'

        self.logger.debug("request_path: '%s'", request_path)

        def _resolve_paths(paths):
            for path in paths[::-1]:
                path = os.path.join(path, request_path)

                if not os.path.exists(path):
                    continue

                if os.path.isdir(path) and self.directory_index:
                    index_path = os.path.join(path, 'index.html')

                    if os.path.exists(index_path):
                        return index_path

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
        media_url = '/' + request_path

        contents = self.context.contents.filter(
            media__passes=lambda m: m and m.filter(url=media_url).exists())

        if contents.exists():
            media_contents = contents.last()['media']
            media_content = media_contents.filter(url=media_url).last()

            self.context.plugins.run_plugin_hook('render_media_content',
                                                 media_content)

            self.logger.debug("handled as media file: '%s'",
                              media_content['path'])

            return os.path.join(self.context.settings.CONTENT_ROOT,
                                media_content['path'])

        # content
        contents = self.context.contents.filter(output=request_path)
        content = None

        if contents.exists():
            content = contents.last()

        elif self.directory_index:  # directory index
            contents = self.context.contents.filter(
                output=os.path.join(request_path, 'index.html')
            )

            if contents.exists():
                content = contents.last()

        if content:
            self.context.plugins.run_plugin_hook('render_content', content)

            self.logger.debug("handled as content: '%s'",
                              content['path'] or content)

            return content

        # pre build layers
        path = _resolve_paths(self.context.settings.PRE_BUILD_LAYERS)

        if path:
            self.logger.debug("handled as pre build layer: '%s'", path)

            return path

    def list_directory(self, path):
        # post build layers
        # static
        # media
        # content
        # pre build layers

        # this has to be an mutable object to be changeable from inline
        # functions
        directory_exists = [False]

        directory_content = {}
        cleaned_path = path

        if cleaned_path.startswith('/'):
            cleaned_path = cleaned_path[1:]

        def _add(name, type_name):
            directory_exists[0] = True

            if name in directory_content:
                directory_content[name] = '{}, {}'.format(
                    directory_content[name],
                    type_name,
                )

            else:
                directory_content[name] = type_name

        def _list_directories(directories, type_base_name):
            for directory in directories:
                root = os.path.join(directory, cleaned_path)

                if not os.path.exists(root):
                    continue

                for i in os.listdir(root):
                    abs_path = os.path.join(root, i)
                    is_dir = os.path.isdir(abs_path)

                    # skip empty directories
                    if is_dir and os.listdir(abs_path) == []:
                        continue

                    name = '{}{}'.format(i, '/' if is_dir else '')
                    type_name = '{}:{}'.format(type_base_name, directory)

                    _add(name, type_name)

        def _list_contents(contents, type_base_name):
            for content in contents:
                if not content['output'] or content['output'] == '/dev/null':
                    continue

                if not content['output'].startswith(cleaned_path):
                    continue

                type_name = '{}:{}'.format(
                    type_base_name,
                    content['path'],
                )

                name = os.path.relpath(
                    '/{}'.format(content['output']),
                    path,
                )

                if '/' in name:
                    name = '{}/'.format([i for i in name.split('/') if i][0])

                _add(name, type_name)

        _list_directories(
            self.context.settings.POST_BUILD_LAYERS, 'post build layer')

        _list_directories(self.static_dirs, 'static')
        _list_contents(self.context.media_contents, 'media')
        _list_contents(self.context.contents, 'content')

        _list_directories(
            self.context.settings.PRE_BUILD_LAYERS, 'pre build layer')

        # directory seems not to be existing
        if not directory_exists[0]:
            return False, ''

        # sort directory content alphabetical, directories first
        directory_content_directories = []
        directory_content_files = []

        for key, value in directory_content.items():
            if key.endswith('/'):
                directory_content_directories.append(
                    (key, value, ),
                )

            else:
                directory_content_files.append(
                    (key, value, ),
                )

        directory_content = [
            *sorted(directory_content_directories, key=lambda v: v[0]),
            *sorted(directory_content_files, key=lambda v: v[0]),
        ]

        # add backlink to parent directory
        if cleaned_path:
            directory_content.insert(0, ('../', os.path.dirname(path), ))

        return True, directory_content

    async def __call__(self, request):
        def _404():
            self.logger.debug('404: not found')

            return Response(text='404: not found', status=404)

        def gen_response(path):
            content = self.resolve(path)

            # fallback
            if (not content or
               isinstance(content, str) and os.path.isdir(content)):

                # 404
                if not self.directory_listing:
                    return _404()

                # directory listing
                directory_exists, directory_content = \
                    self.list_directory(request.path)

                if not directory_exists:
                    return _404()

                template = Template(open(DIRECTORY_LIST_HTML, 'r').read())

                text = template.render(
                    path=request.path,
                    directory_content=directory_content,
                )

                return Response(text=text, status=200,
                                content_type='text/html')

            # file response
            if isinstance(content, str):
                return FileResponse(content)

            # content response
            if content['redirect']:
                raise HTTPFound(content['redirect'])

            try:
                output = self.context.render(content)
                self.history.append(content)

            except Exception as e:
                self.context.logger.error(e, exc_info=True)

                return Response(text='500: rendering error', status=500)

            return Response(text=output, content_type='text/html')

        try:
            response = await self.server.loop.run_in_executor(
                self.server.executor,
                gen_response,
                request.path
            )

        except CancelledError:
            response = Response(text='499: Client Closed Request', status=499)

        except Exception as e:
            if isinstance(e, HTTPFound):  # redirects
                raise

            self.context.logger.error(e, exc_info=True)

            response = Response(text='500: Internal Error', status=500)

        return response
