import logging
import os
import shutil
from configparser import RawConfigParser
from copy import deepcopy

import docutils
import sphinx
from jinja2 import Environment, FileSystemLoader
from pkg_resources import iter_entry_points
from sphinx.config import Config
from sphinx.jinja2glue import _tobool, _todim, _toint
from sphinx.registry import SphinxComponentRegistry
from sphinx.theming import HTMLThemeFactory, Theme


SPHINX_THEME_ROOT = os.path.join(os.path.dirname(sphinx.__file__), 'themes')

logger = logging.getLogger('flamingo.plugins.SphinxThemes')


class SphinxThemeNotFoundError(Exception):
    pass


class SphinxConfigRecursionError(Exception):
    pass


class SphinxApp:
    def __init__(self):
        self.registry = SphinxComponentRegistry()
        themes = self.discover_themes()
        for theme_name in themes.keys():
            self.registry.add_html_theme(theme_name, themes[theme_name])
        self.config = Config()

    def discover_themes(self):
        themes = {}

        logger.debug('discovering sphinx themes')

        # discover sphinx default themes
        for name in os.listdir(SPHINX_THEME_ROOT):
            theme_path = os.path.join(SPHINX_THEME_ROOT, name)

            if not os.path.isdir(theme_path):
                continue

            themes[name] = theme_path

        # discover 3rd party themes from pkg resources
        for entry_point in iter_entry_points('sphinx.html_themes'):
            name = entry_point.name
            module = entry_point.load()
            theme_path = os.path.dirname(module.__file__)

            themes[name] = theme_path

        logger.debug('discovered sphinx themes: %s', ', '.join(themes.keys()))

        return themes


class SphinxThemeConfig:
    def __init__(self, theme_name, app, option_overrides={}):
        logger.debug("setting up sphinx theme config for '%s'", theme_name)

        self.theme_name = theme_name
        self.option_overrides = option_overrides
        self.app = app

        self.hierarchy = self._gen_hierarchy()
        self.config = RawConfigParser()

        for name in self.hierarchy:
            config_path = self._gen_theme_config_path(name)

            logger.debug('reading %s', config_path)

            self.config.read(config_path)

    def _gen_theme_config_path(self, name):
        return os.path.join(self.app.registry.html_themes[name], 'theme.conf')

    def _gen_hierarchy(self):
        hierarchy = [self.theme_name]
        inherit = self.theme_name

        while True:
            config_path = self._gen_theme_config_path(inherit)
            config = RawConfigParser()

            config.read(config_path)

            inherit = config.get('theme', 'inherit')

            if inherit == 'none':
                return hierarchy

            if inherit in hierarchy:
                raise SphinxConfigRecursionError(
                    ' -> '.join(hierarchy + [inherit]))

            hierarchy.insert(0, inherit)

    def get_theme_config(self):
        return {
            'stylesheet': self.config.get('theme', 'stylesheet'),

            'sidebars': [
                i.strip()
                for i in self.config.get('theme', 'sidebars').split(',')
            ],
        }

    def get_raw_theme_options(self):
        raw_options = {}

        for option_name in self.config.options('options'):
            raw_options[option_name] = self.config.get('options', option_name)

        raw_options.update(self.option_overrides)

        return raw_options

    def get_theme_options(self):
        raw_options = self.get_raw_theme_options()
        options = {}

        for raw_option_name, value in raw_options.items():
            option_name = 'theme_{}'.format(raw_option_name)
            options[option_name] = value

        return options


class SphinxTheme:
    def __init__(self, name, build_dir, setup=True, options={}):
        self.name = name
        self.build_dir = build_dir

        self.app = SphinxApp()

        if name not in self.app.registry.html_themes:
            raise SphinxThemeNotFoundError(
                "sphinx theme '{}' not found. available themes: {}".format(
                    name,
                    ', '.join(["'{}'".format(i)
                               for i in self.app.registry.html_themes.keys()])
                )
            )

        self.config = SphinxThemeConfig(
            name,
            self.app,
            option_overrides=options,
        )

        self.factory = HTMLThemeFactory(app=self.app)

        self.theme = Theme(
            name=name,
            theme_path=self.app.registry.html_themes[name],
            factory=self.factory,
        )

        if setup:
            self.setup()

    def rm(self, path):
        logger.debug('rm -rf %s', path)

        if os.path.isdir(path):
            return shutil.rmtree(path)

        return os.unlink(path)

    def cp(self, source, destination):
        logger.debug('cp -r %s %s', source, destination)

        if os.path.isdir(source):
            return shutil.copytree(source, destination)

        return shutil.copy(source, destination)

    def gen_static_file_template_context(self):
        if not self._static_file_template_context_cache:
            self._static_file_template_context_cache = {
                **self.config.get_theme_options(),
            }
            self._static_file_template_context_cache['docutils_version_info'] = docutils.__version_info__[:5]

        return deepcopy(self._static_file_template_context_cache)

    def setup(self):
        logger.debug('setting up flamingo theme')

        # paths
        self.template_root = os.path.join(self.build_dir, 'templates')
        self.static_root = os.path.join(self.build_dir, 'static')

        os.makedirs(self.template_root)
        os.makedirs(self.static_root)

        # setup sphinx like static file rendering environment
        self._static_file_template_context_cache = {}

        self.jinja2_env = Environment(
            loader=FileSystemLoader(
                self.theme.get_theme_dirs(),
                followlinks=True
            )
        )

        self.jinja2_env.filters['tobool'] = _tobool
        self.jinja2_env.filters['todim'] = _todim
        self.jinja2_env.filters['toint'] = _toint

        # setup temporary flamingo theme dir
        for theme_dir in self.theme.get_theme_dirs()[::-1]:
            # templates

            # copy full theme namespace first to make absolute template
            # paths work
            theme_name = os.path.basename(theme_dir)
            theme_output = os.path.join(self.template_root, theme_name)

            shutil.copytree(theme_dir, theme_output)

            # remove static directories and configs from template root
            theme_static_dir = os.path.join(theme_output, 'static')
            theme_config = os.path.join(theme_output, 'theme.conf')

            if os.path.exists(theme_static_dir):
                self.rm(theme_static_dir)

            if os.path.exists(theme_config):
                self.rm(theme_config)

            # stack themes to emulate a file system loader
            for i in os.listdir(theme_dir):
                if i in ('static', 'theme.conf'):
                    continue

                source = os.path.join(theme_dir, i)
                destination = os.path.join(self.template_root, i)

                self.cp(source, destination)

            # static files
            static_dir = os.path.join(theme_dir, 'static')

            if not os.path.exists(static_dir):
                continue

            for root, dirs, files in os.walk(static_dir):
                for f in files:
                    source = os.path.join(root, f)

                    destination = os.path.join(
                        self.static_root,
                        os.path.relpath(source, static_dir),
                    )

                    destination_dirname = os.path.dirname(destination)

                    if not os.path.exists(destination_dirname):
                        os.makedirs(destination_dirname)

                    # regular files
                    if not source.endswith('_t'):
                        self.cp(source, destination)

                        continue

                    # template static files
                    logger.debug('rendering %s -> %s', source, destination)

                    template_name = os.path.relpath(source, theme_dir)
                    template = self.jinja2_env.get_template(template_name)
                    template_context = self.gen_static_file_template_context()

                    with open(destination[:-2], 'w+') as f:
                        f.write(template.render(**template_context))

                    continue

    def __repr__(self):
        return "<SphinxTheme('{}', {})>".format(self.name, self.build_dir)
