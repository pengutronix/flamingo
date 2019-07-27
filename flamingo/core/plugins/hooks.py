import logging

logger = logging.getLogger('flamingo.hooks')

HOOK_NAMES = [
    'parser_setup',
    'content_parsed',
    'contents_parsed',
    'templating_engine_setup',
    'context_setup',
    'pre_build',
    'post_build',
]


def hook(name):
    def decorator(function):
        if name not in HOOK_NAMES:
            logger.warn("hook '%s' is unknown", name)

        function.flamingo_hook_name = name

        return function

    return decorator


class Hooks:
    def __init__(self, context):
        self._hooks = {
            'parser_setup': [],
            'content_parsed': [],
            'contents_parsed': [],
            'templating_engine_setup': [],
            'context_setup': [],
            'pre_build': [],
            'post_build': [],
        }

        for attr_name in dir(context.settings):
            attr = getattr(context.settings, attr_name)

            if hasattr(attr, 'flamingo_hook_name'):
                self._hooks[attr.flamingo_hook_name].append(attr)

        self._dir = super().__dir__()

        for key in self._hooks.keys():
            if not self._hooks[key]:
                self._dir.remove(key)

    def run_hooks(self, name, context, *args):
        for hook in self._hooks[name]:
            logger.debug('%s: running %s', name, hook)
            hook(context, *args)

    def parser_setup(self, context):
        self.run_hooks('parser_setup', context)

    def content_parsed(self, context, content):
        self.run_hooks('content_parsed', context, content)

    def contents_parsed(self, context):
        self.run_hooks('contents_parsed', context)

    def templating_engine_setup(self, context, templating_engine):
        self.run_hooks('templating_engine_setup', context, templating_engine)

    def context_setup(self, context):
        self.run_hooks('context_setup', context)

    def pre_build(self, context):
        self.run_hooks('pre_build', context)

    def post_build(self, context):
        self.run_hooks('post_build', context)

    def __dir__(self):
        return self._dir
