import logging
import shutil
import os

from flamingo.core.parser import FileParser, ParsingError
from flamingo.core.data_model import ContentSet, Content
from flamingo.core.utils.imports import acquire


class Context:
    def __init__(self, settings):
        self.settings = settings

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
        self.parser = FileParser()
        self.run_plugin_hook('parser_setup')

        # parse contents
        self.contents = ContentSet()
        self.content = None

        self._media = []  # FIXME: this should be part of Content()

        for path in self.get_source_paths():
            self.logger.debug("reading %s ", path)

            try:
                self.content = Content(
                    path=os.path.relpath(path, settings.CONTENT_ROOT))

                self.parser.parse(path, self.content)

                self.run_plugin_hook('content_parsed', self.content)

                self.contents.add(self.content)

            except ParsingError as e:
                self.logger.error('%s: %s', path, e)

            except Exception:
                self.logger.error('exception occoured while reading %s',
                                  path, exc_info=True)

        del self.content
        self.run_plugin_hook('contents_parsed')

        # setup templating engine
        templating_engine_class = acquire(settings.TEMPLATING_ENGINE)

        self.templating_engine = templating_engine_class(
            settings.THEME_PATHS + settings.CORE_THEME_PATHS
        )

        self.run_plugin_hook('templating_engine_setup', self.templating_engine)
        self.run_plugin_hook('context_setup')

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
            self.logger.debug("searching content recursive in %s",
                              self.settings.CONTENT_ROOT)

            for root, dirs, files in os.walk(self.settings.CONTENT_ROOT):
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
        }

        return self.templating_engine.render(template_name, template_context)

    def copy_media(self, filename, content_source_path):
        # gen source_path
        if filename.startswith('/'):
            source_path = os.path.join(
                self.settings.CONTENT_ROOT, filename[1:])

        else:
            source_path = os.path.join(
                os.path.dirname(
                    os.path.join(self.settings.CONTENT_ROOT,
                                 content_source_path)
                ),
                filename,
            )

        source_path = os.path.normpath(source_path)

        # gen destination_path
        destination_path = os.path.join(
            self.settings.MEDIA_ROOT,
            os.path.relpath(source_path, self.settings.CONTENT_ROOT),
        )

        # gen link
        link = os.path.join(
            '/media',
            os.path.relpath(destination_path, self.settings.MEDIA_ROOT),
        )

        # check if media exists
        if not os.path.exists(source_path):
            self.logger.critical(
                "media '%s' does not exist (used as '%s' in '%s')",
                source_path, filename, content_source_path,
            )

        else:
            self._media.append((source_path, destination_path, ))

        return source_path, destination_path, link

    def build(self, clean=True):
        self.run_plugin_hook('pre_build')

        def makedirs(path):
            dirname = os.path.dirname(path)

            if not os.path.exists(dirname):
                self.logger.debug('mkdir -p %s', dirname)
                os.makedirs(dirname)

        # remove previous artifacts
        if clean and os.path.exists(self.settings.OUTPUT_ROOT):
            self.logger.debug('rm -rf %s', self.settings.OUTPUT_ROOT)
            shutil.rmtree(self.settings.OUTPUT_ROOT)

        # render contents
        for content in self.contents:
            output_path = os.path.join(self.settings.OUTPUT_ROOT,
                                       content['output'])

            makedirs(output_path)

            # render and write content
            with open(output_path, 'w+') as f:
                self.logger.debug("writing '%s'...", output_path)

                if content['template']:
                    output = self.render(content)

                else:
                    output = content['content']

                f.write(output)

        if self.settings.CONTENT_PATHS:
            return

        # copy media
        for source_path, destination_path in self._media:
            makedirs(destination_path)
            self.logger.debug('cp %s %s', source_path, destination_path)
            shutil.copy(source_path, destination_path)

        # copy static
        for static_dir in self.templating_engine.find_static_dirs():
            for root, dirs, files in os.walk(static_dir):
                for f in files:
                    src = os.path.join(root, f)

                    dst = os.path.join(
                        self.settings.STATIC_ROOT,
                        os.path.relpath(root, static_dir),
                        f,
                    )

                    self.logger.debug('cp %s %s', src, dst)

                    makedirs(dst)
                    shutil.copy(src, dst)

        self.run_plugin_hook('post_build')
