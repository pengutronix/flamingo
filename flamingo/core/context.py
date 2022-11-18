import logging
import shutil
import os

from flamingo.core.data_model import ContentSet, AND, NOT, OR, Q, F
from flamingo.core.plugins.plugin_manager import PluginManager
from flamingo.core.parser import FileParser, ParsingError
from flamingo.core.plugins.media import add_media
from flamingo.core.utils.imports import acquire
from flamingo.core.types import OverlayObject


class Context(OverlayObject):
    __overlay_ignore_attributes = [
        'content',
        'contents',
    ]

    def __init__(self, settings, contents=None, setup=True):
        super().__init__()

        self.settings = settings
        self.contents = contents
        self.content = None
        self.plugins = None

        if setup:
            self.setup()

    def setup(self):
        self.errors = []

        # setup logging
        self.logger = logging.getLogger('flamingo')
        self.logger.debug('setting up context')

        # setup plugins
        self.plugins = PluginManager(self)
        self.plugins.run_plugin_hook('setup')
        self.plugins.run_plugin_hook('settings_setup')

        # setup parser
        self.parser = FileParser(context=self)
        self.plugins.run_plugin_hook('parser_setup')

        # setup templating engine
        templating_engine_class, path = acquire(
            self.settings.TEMPLATING_ENGINE)

        self.templating_engine = templating_engine_class(self)

        self.plugins.run_plugin_hook('templating_engine_setup',
                                     self.templating_engine)

        # parse contents
        self.contents = self.contents or ContentSet()
        self.parse_all()

        # context ready
        self.plugins.run_plugin_hook('context_setup')

    def resolve_content_path(self, path, content=None):
        """
        supported formats:

            index.rst           relative path (only available if self.content
                                               is set or content is given)

            /index.rst          absolute path
            content/index.rst   absolute path with CONTENT_ROOT given without /
            /content/index.rst  absolute path with CONTENT_ROOT given with /
        """

        current_content = content or self.content

        def _try_relative_path(path):
            path = os.path.join(os.path.dirname(current_content['path']), path)
            content_set = self.contents.filter(path=path)

            if content_set.exists():
                return content_set.get()

        def _try_absolute_path(path):
            if path.startswith('/'):
                path = path[1:]

            if path.startswith(self.settings.CONTENT_ROOT):
                path = os.path.relpath(path, self.settings.CONTENT_ROOT)

            content_set = self.contents.filter(path=path)

            if content_set.exists():
                return content_set.get()

        # relative paths
        if current_content and not path.startswith('/'):
            content = _try_relative_path(path)

            if content:
                return content

        # try absolute
        content = _try_absolute_path(path)

        if content:
            return content

    @property
    def media_contents(self):
        _media_contents = ContentSet()

        if self.contents:
            for content in self.contents:
                if not content['media']:
                    continue

                _media_contents.add(*content['media'])

        return _media_contents

    def parse(self, content):
        previous_content = self.content
        self.content = content
        path = os.path.join(self.settings.CONTENT_ROOT, content['path'])

        self.logger.debug("reading %s ", path)

        try:
            self.parser.parse(path, content)

            self.plugins.run_plugin_hook('content_parsed', content)

        except ParsingError as e:
            content['_parsing_error'] = e
            self.errors.append(e)

            if hasattr(e, 'line'):
                line = e.line

                if content['content_offset']:
                    line += content['content_offset']

                self.logger.error('%s:%s: %s', path, line, e)

            else:
                self.logger.error('%s: %s', path, e)

        except Exception as e:
            content['_parsing_error'] = e
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

        self.plugins.run_plugin_hook('contents_parsed')

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

    def gen_template_context(self, **extra_context):
        return {
            'context': self,
            'AND': AND,
            'NOT': NOT,
            'OR': OR,
            'Q': Q,
            'F': F,
            **self.settings.EXTRA_CONTEXT,
            **extra_context,
        }

    def pre_render(self, content, template_context=None):
        if (not self.settings.PRE_RENDER_CONTENT or
            not content.get('is_template', True) or
           content['_content_body_rendered']):

            return True, content['content_body']

        self.logger.debug('pre rendering %s', content['path'] or content)

        if template_context is None:
            template_context = self.gen_template_context(content=content)

        try:
            return self.templating_engine.pre_render_content(
                content=content,
                template_context=template_context,
            )

        except Exception as e:
            self.logger.error(
                '%s: exception raised while pre rendering content',
                content['path'],
                exc_info=True,
            )

            self.errors.append(e)

        return False, ''

    def render(self, content, template_name=''):
        template_name = template_name or content['template']

        self.logger.debug('rendering %s using %s', content['path'] or content,
                          template_name)

        if not template_name:
            content['template_context'] = {}

            return content['content_body'] or ''

        template_context = self.gen_template_context(content=content)

        exitcode, output = self.pre_render(
            content=content,
            template_context=template_context,
        )

        if exitcode:
            content['content_body'] = output
            content['_content_body_rendered'] = True

        else:
            return output

        self.plugins.run_hook('template_context_setup',
                              content, template_name, template_context)

        output = self.templating_engine.render(template_name, template_context)
        content['template_context'] = template_context

        return output

    def rm_rf(self, path, force=False):
        if self.settings.SKIP_FILE_OPERATIONS and not force:
            return

        self.logger.debug('rm -rf %s', path)

        if os.path.isdir(path):
            shutil.rmtree(path)

        else:
            os.unlink(path)

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

    def add_media(self, name, content=None, **extra_meta_data):
        content = content or self.content

        return add_media(name=name, context=self, content=content,
                         **extra_meta_data)

    def build(self, clean=True):
        # remove previous artifacts
        if clean and os.path.exists(self.settings.OUTPUT_ROOT):
            self.rm_rf(self.settings.OUTPUT_ROOT)

        # run pre build hooks
        self.plugins.run_plugin_hook('pre_build')

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

        self.plugins.run_plugin_hook('post_build')
