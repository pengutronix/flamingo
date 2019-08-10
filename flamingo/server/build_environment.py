from copy import deepcopy

from flamingo.core.context import Context


class BuildEnvironment:
    def __init__(self, settings):
        # configure
        settings.LIVE_SERVER_RUNNING = True
        settings.SKIP_FILE_OPERATIONS = True
        settings.CONTENT_PATHS = []

        settings.SKIP_HOOKS = [
            'content_parsed',
            'contents_parsed',
            'pre_build',
            'post_build',
        ]

        # setup context and contents
        self.context = Context(settings=settings)
        self.raw_contents = deepcopy(self.context.contents)

        # configure
        self.context.settings.SKIP_HOOKS = []

        # enable overlays
        self.context.overlay_enable()
        self.context.settings.overlay_enable()

        # fake initial build
        for content in self.context.contents:
            self.context.content = content
            self.context.run_plugin_hook('content_parsed', content)

        self.context.run_plugin_hook('contents_parsed')
        self.context.run_plugin_hook('pre_build')
        self.context.run_plugin_hook('post_build')

    def build(self, paths):
        # reset
        self.context.overlay_reset()
        self.context.settings.overlay_reset()
        self.raw_contents = self.raw_contents.exclude(path__in=paths)
        self.context.contents = deepcopy(self.raw_contents)

        # build
        self.context.settings.CONTENT_PATHS = paths

        self.context.parse_all()
        self.context.run_plugin_hook('pre_build')
        self.context.run_plugin_hook('post_build')
        self.context.settings.overlay_reset()
