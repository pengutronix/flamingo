import logging
import shutil
import os

from flamingo.core.data_model import ContentSet, AND, NOT, OR, Q, F
from flamingo.core.parser import FileParser, ParsingError
from flamingo.core.utils.imports import acquire
from flamingo.core.types import OverlayObject


class Context(OverlayObject):
    __overlay_ignore_attributes = [
        'content',
        'contents',
    ]

    def __init__(self, settings, contents=None):
        super().__init__()

        self.settings = settings
        self.errors = []

        # setup logging
        self.logger = logging.getLogger('flamingo')
        self.logger.debug('setting up context')

        # setup plugins
        self.plugins = []
        self.plugin_paths = []

        plugins = (self.settings.CORE_PLUGINS_PRE +
                   self.settings.DEFAULT_PLUGINS +
                   self.settings.PLUGINS +
                   self.settings.CORE_PLUGINS_POST)

        for plugin in plugins:
            self.logger.debug("setting up plugin '%s' ", plugin)

            try:
                plugin_class, plugin_path = acquire(plugin)

                if plugin == 'flamingo.core.plugins.Hooks':
                    self.plugins.append(plugin_class(self))

                else:
                    self.plugins.append(plugin_class())

                self.plugin_paths.append(plugin_path)

            except Exception:
                self.logger.error('plugin setup failed', exc_info=True)

        self.plugin_paths = list(set(self.plugin_paths))

        # discover plugin hooks
        self._plugin_hooks = {
            'parser_setup': [],
            'content_parsed': [],
            'contents_parsed': [],
            'templating_engine_setup': [],
            'context_setup': [],
            'pre_build': [],
            'post_build': [],

            # live-server hooks
            'render_content': [],
            'render_media_content': [],
        }

        hook_names = self._plugin_hooks.keys()

        for plugin in self.plugins:
            for hook_name in hook_names:
                if hook_name not in dir(plugin):
                    continue

                hook = getattr(plugin, hook_name)

                if hook:
                    self._plugin_hooks[hook_name].append(
                        (plugin.__class__.__name__, hook, )
                    )

        # setup parser
        self.parser = FileParser(context=self)
        self.run_plugin_hook('parser_setup')

        # parse contents
        self.contents = contents or ContentSet()
        self.parse_all()

        # setup templating engine
        templating_engine_class, path = acquire(settings.TEMPLATING_ENGINE)

        self.templating_engine = templating_engine_class(
            settings.THEME_PATHS +
            sum([getattr(i, 'THEME_PATHS', []) for i in self.plugins], []) +
            settings.CORE_THEME_PATHS
        )

        self.run_plugin_hook('templating_engine_setup', self.templating_engine)
        self.run_plugin_hook('context_setup')

    def parse(self, content):
        previous_content = self.content
        self.content = content
        path = os.path.join(self.settings.CONTENT_ROOT, content['path'])

        self.logger.debug("reading %s ", path)

        try:
            self.parser.parse(path, content)

            self.run_plugin_hook('content_parsed', content)

        except ParsingError as e:
            self.errors.append(e)

            if hasattr(e, 'line'):
                line = e.line

                if content['content_offset']:
                    line += content['content_offset']

                self.logger.error('%s:%s: %s', path, line, e)

            else:
                self.logger.error('%s: %s', path, e)

        except Exception as e:
            self.errors.append(e)

            self.logger.error('exception occoured while reading %s',
                              content['path'], exc_info=True)

        finally:
            self.content = previous_content

    def parse_all(self):
        self.content = None

        for path in self.get_source_paths():
            self.contents.add(
                path=os.path.relpath(path, self.settings.CONTENT_ROOT))

        for content in self.contents:
            if content['content_body']:
                continue

            self.parse(content)

        self.content = None

        self.run_plugin_hook('contents_parsed')

    def get_source_paths(self):
        self.logger.debug('searching for content')

        supported_extensions = self.parser.get_extensions()

        if self.settings.CONTENT_PATHS:
            self.logger.debug('using user defined content paths')

            for path in self.settings.CONTENT_PATHS:
                path = os.path.join(self.settings.CONTENT_ROOT, path)

                if not os.path.exists(path):
                    continue

                extension = os.path.splitext(path)[1][1:]

                if extension not in supported_extensions:
                    self.logger.debug(
                        "skipping '%s'. extension '%s' is not supported",
                        path, extension)

                    continue

                yield path

        else:
            self.logger.debug(
                "searching content with extension %s recursive in %s",
                repr(supported_extensions), self.settings.CONTENT_ROOT,
            )

            for root, dirs, files in os.walk(
                    self.settings.CONTENT_ROOT,
                    followlinks=self.settings.FOLLOW_LINKS):

                for name in files:
                    extension = os.path.splitext(name)[1][1:]

                    if extension not in supported_extensions:
                        continue

                    yield os.path.join(root, name)

    def run_plugin_hook(self, name, *args, **kwargs):
        if name in self.settings.SKIP_HOOKS:
            return

        if name not in self._plugin_hooks:
            return

        if not self._plugin_hooks[name]:
            return

        self.logger.debug("running plugin hook '%s'", name)

        for plugin_name, hook in self._plugin_hooks[name]:
            self.logger.debug('running %s.%s', plugin_name, name)

            try:
                hook(self, *args, **kwargs)

            except Exception as e:
                self.logger.error(e, exc_info=True)

    def render(self, content, template_name=''):
        template_name = template_name or content['template']

        if not template_name:
            content['template_context'] = {}

            return content['content_body'] or ''

        template_context = {
            'content': content,
            'context': self,
            'AND': AND,
            'NOT': NOT,
            'OR': OR,
            'Q': Q,
            'F': F,
            **self.settings.EXTRA_CONTEXT,
        }

        if self.settings.PRE_RENDER_CONTENT:
            content['content_body'] = self.templating_engine.render_string(
                content['content_body'], template_context)

        output = self.templating_engine.render(template_name, template_context)
        content['template_context'] = template_context

        return output

    def rm_rf(self, path, force=False):
        if self.settings.SKIP_FILE_OPERATIONS and not force:
            return

        self.logger.debug('rm -rf %s', self.settings.OUTPUT_ROOT)
        shutil.rmtree(path)

    def mkdir_p(self, path, force=False):
        if self.settings.SKIP_FILE_OPERATIONS and not force:
            return

        dirname = os.path.dirname(path)

        if not os.path.exists(dirname):
            self.logger.debug('mkdir -p %s', dirname)
            os.makedirs(dirname)

    def cp(self, source, destination, force=False):
        if self.settings.SKIP_FILE_OPERATIONS and not force:
            return

        self.mkdir_p(destination)
        self.logger.debug('cp %s %s', source, destination)
        shutil.copy(source, destination)

    def write(self, path, text, mode='w+', force=False):
        if self.settings.SKIP_FILE_OPERATIONS and not force:
            return

        self.logger.debug("writing '%s", path)

        with open(path, mode) as f:
            f.write(text)

    def build(self, clean=True):
        self.run_plugin_hook('pre_build')

        # remove previous artifacts
        if clean and os.path.exists(self.settings.OUTPUT_ROOT):
            self.rm_rf(self.settings.OUTPUT_ROOT)

        # render contents
        if self.settings.CONTENT_PATHS:
            contents = self.contents.filter(
                Q(path__in=self.settings.CONTENT_PATHS) |
                Q(i18n_path__in=self.settings.CONTENT_PATHS),
            )

        else:
            contents = self.contents

        for content in contents:
            output_path = os.path.join(self.settings.OUTPUT_ROOT,
                                       content['output'])

            self.mkdir_p(output_path)
            self.write(output_path, self.render(content))

        self.run_plugin_hook('post_build')
