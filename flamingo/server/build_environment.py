from functools import partial
from copy import deepcopy
import asyncio
import logging
import os

from flamingo.core.utils.cli import start_editor
from flamingo.core.context import Context

logger = logging.getLogger('flamingo.server.BuildEnvironment')


class BuildEnvironment:
    def __init__(self, server, setup=True):
        self.server = server
        self.context = None

        self.pending = {
            '*': [],
        }

        if setup:
            self.setup()

    def setup(self):
        # configure
        self.server.settings.LIVE_SERVER_RUNNING = True
        self.server.settings.SKIP_FILE_OPERATIONS = True
        self.server.settings.CONTENT_PATHS = []

        self.server.settings.SKIP_HOOKS = [
            'content_parsed',
            'contents_parsed',
            'pre_build',
            'post_build',
        ]

        # setup context and contents
        self.context = Context(settings=self.server.settings, setup=False)
        self.context.setup()

        self.raw_contents = deepcopy(self.context.contents)

        # configure
        self.context.settings.SKIP_HOOKS = []

        # enable overlays
        self.context.overlay_enable()
        self.context.settings.overlay_enable()

        # fake initial build
        for content in self.context.contents:
            self.context.content = content
            self.context.plugins.run_plugin_hook('content_parsed', content)

        self.context.plugins.run_plugin_hook('contents_parsed')
        self.context.plugins.run_plugin_hook('pre_build')
        self.context.plugins.run_plugin_hook('post_build')

        self.patch_contents()

    def build(self, paths):
        self.server.rpc_logging_handler.filter(paths)

        logger.debug('rebuilding %s', paths)

        # reset
        logger.debug('resetting context overlay')
        self.context.overlay_reset()

        logger.debug('resetting settings overlay')
        self.context.settings.overlay_reset()

        self.raw_contents = self.raw_contents.exclude(path__in=paths)

        # find new contents
        self.context.settings.CONTENT_PATHS = paths

        source_paths = [
            os.path.relpath(i, self.context.settings.CONTENT_ROOT)
            for i in self.context.get_source_paths()
        ]

        for path in source_paths:
            self.raw_contents.add(path=path)

        # parse
        self.context.settings.SKIP_HOOKS = ['content_parsed']

        for content in self.raw_contents:
            if content['path'] not in source_paths:
                continue

            if content['content_body']:
                continue

            self.context.parse(content)

        # run hooks
        self.context.contents = deepcopy(self.raw_contents)

        for content in self.context.contents:
            if content['path'] not in source_paths:
                continue

            self.context.content = content
            self.context.plugins.run_plugin_hook('content_parsed', content)

        self.context.content = None

        self.context.plugins.run_plugin_hook('contents_parsed')
        self.context.plugins.run_plugin_hook('pre_build')
        self.context.plugins.run_plugin_hook('post_build')

        # finish
        self.context.settings.CONTENT_PATHS = []
        self.context.settings.SKIP_HOOKS = []

        self.patch_contents()

        while self.pending['*']:
            future = self.pending['*'].pop()
            self.server.loop.call_soon_threadsafe(future.set_result, True)

        for path in paths:
            if path in self.pending:
                future = self.pending.pop(path)
                self.server.loop.call_soon_threadsafe(future.set_result, True)

    def patch_contents(self):
        logger.debug('patch Contents')

        for content in self.context.contents:
            # content.edit
            if content['path']:
                path = os.path.join(self.server.settings.CONTENT_ROOT,
                                    content['path'])

                content.edit = partial(start_editor, path)

            else:
                content.edit = partial(print, 'Content has no source file')

            # content.show
            if content['url']:
                content.show = partial(
                    self.server.frontend_controller.set_url, content)

            else:
                content.show = partial(print, 'Content has no url')

    def await_rebuild(self, paths=None):
        futures = []

        if isinstance(paths, str):
            paths = [paths]

        if paths:
            for path in paths:
                if path == '*':
                    raise ValueError("'*' is a reserved value")

                if path not in self.pending:
                    self.pending[path] = asyncio.Future(loop=self.server.loop)

                futures.append(self.pending[path])

        else:
            future = asyncio.Future(loop=self.server.loop)
            futures.append(future)

            self.pending['*'].append(future)

        return asyncio.gather(*futures, loop=self.server.loop)
