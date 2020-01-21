from functools import partial
from copy import deepcopy
import logging
import os

from flamingo.core.utils.cli import start_editor
from flamingo.core.context import Context

logger = logging.getLogger('flamingo.server.BuildEnvironment')


class BuildEnvironment:
    def __init__(self, server):
        self.server = server

        # configure
        server.settings.LIVE_SERVER_RUNNING = True
        server.settings.SKIP_FILE_OPERATIONS = True
        server.settings.CONTENT_PATHS = []

        server.settings.SKIP_HOOKS = [
            'content_parsed',
            'contents_parsed',
            'pre_build',
            'post_build',
        ]

        # setup context and contents
        self.context = Context(settings=server.settings)
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
        logger.debug('rebuilding %s', paths)

        # reset
        logger.debug('resetting context overlay')
        self.context.overlay_reset()

        logger.debug('resetting settings overlay')
        self.context.settings.overlay_reset()

        self.raw_contents = self.raw_contents.exclude(path__in=paths)
        self.context.contents = deepcopy(self.raw_contents)

        # build
        self.context.settings.CONTENT_PATHS = paths

        self.context.plugins.run_plugin_hook('setup')
        self.context.plugins.run_plugin_hook('settings_setup')

        self.context.parse_all()

        self.context.plugins.run_plugin_hook('pre_build')
        self.context.plugins.run_plugin_hook('post_build')

        self.patch_contents()

    def Content_on_change_handler(self, content, key, item):
        if key == 'template_context':
            return

        if not content['url']:
            return

        self.server.rpc.notify('status', {
            'changed_paths': content['url'],
        })

    def patch_contents(self):
        logger.debug('patch Contents')

        for content in self.context.contents:
            content.on_change = self.Content_on_change_handler

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
