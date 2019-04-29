import logging
import os

from flamingo.core.data_model import ContentSet, AND, NOT, OR, Q, F
from flamingo.core.parser import FileParser, ParsingError
from flamingo.core.utils.files import mkdir_p, rm_rf, cp
from flamingo.core.utils.imports import acquire


class Context:
    def __init__(self, settings, contents=None):
        self.settings = settings
        self.errors = []

        # setup logging
        self.logger = logging.getLogger('flamingo')
        self.logger.debug('setting up context')

        # setup plugins
        self.plugins = []
        plugins = (self.settings.CORE_PLUGINS +
                   self.settings.DEFAULT_PLUGINS +
                   self.settings.PLUGINS)

        for plugin in plugins:
            self.logger.debug("setting up plugin '%s' ", plugin)

            try:
                plugin_class = acquire(plugin)
                self.plugins.append(plugin_class())

            except Exception:
                self.logger.error('plugin setup failed', exc_info=True)

        # setup parser
        self.parser = FileParser(context=self)
        self.run_plugin_hook('parser_setup')

        # parse contents
        self.contents = contents or ContentSet()
        self.content = None

        for path in self.get_source_paths():
            self.contents.add(
                path=os.path.relpath(path, settings.CONTENT_ROOT))

        for content in self.contents:
            if content['content_body']:
                continue

            self.parse(content)

        self.content = None

        self.run_plugin_hook('contents_parsed')

        # setup templating engine
        templating_engine_class = acquire(settings.TEMPLATING_ENGINE)

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

    def get_source_paths(self):
        self.logger.debug('searching for content')

        supported_extensions = self.parser.get_extensions()

        if self.settings.CONTENT_PATHS:
            self.logger.debug('using user defined content paths')

            for path in self.settings.CONTENT_PATHS:
                path = os.path.join(self.settings.CONTENT_ROOT, path)
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
        self.logger.debug("running plugin hook '%s'", name)

        for plugin in self.plugins:
            hook = getattr(plugin, name, None)

            if not hook:
                continue

            self.logger.debug('running %s.%s', plugin.__class__.__name__, name)
            hook(self, *args, **kwargs)

    def render(self, content, template_name=''):
        template_name = template_name or content['template']

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

        return output, template_context

    def build(self, clean=True, mkdir_p=mkdir_p, cp=cp):
        self.run_plugin_hook('pre_build')

        # remove previous artifacts
        if clean and os.path.exists(self.settings.OUTPUT_ROOT):
            rm_rf(self, self.settings.OUTPUT_ROOT)

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

            mkdir_p(self, output_path)

            # render and write content
            with open(output_path, 'w+') as f:
                self.logger.debug("writing '%s'...", output_path)

                if content['template']:
                    output, template_context = self.render(content)
                    content['template_context'] = template_context

                else:
                    output = content['content']

                output = output or ''

                f.write(output)

        self.run_plugin_hook('post_build')
