import argparse
import logging
import os

import coloredlogs

from flamingo.core.settings import Settings

logger = logging.getLogger('flamingo')


def gen_default_parser(*parser_args, **parser_kwargs):
    parser = argparse.ArgumentParser(*parser_args, **parser_kwargs)

    parser.add_argument('-s', '--settings', nargs='+')
    parser.add_argument('-c', '--content-root', type=str)
    parser.add_argument('-p', '--project-root', type=str)
    parser.add_argument('--content-paths', type=str, nargs='+')

    parser.add_argument(
        '-l', '--log-level',
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
        default='INFO',
    )

    parser.add_argument('-d', '--debug', action='store_true')

    return parser


def parse_args(parser=None):
    parser = parser or gen_default_parser()
    namespace = parser.parse_args()
    settings = Settings()

    # loglevel / debug mode
    log_level = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'FATAL': logging.FATAL,
    }[namespace.log_level]

    if namespace.debug:
        settings.DEBUG = True
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)
    coloredlogs.install(level=log_level)

    # project root
    if namespace.project_root:
        logger.debug('project-root is set')

        # content root
        content_root = os.path.join(namespace.project_root, 'content')

        if os.path.exists(content_root):
            settings.CONTENT_ROOT = content_root

        # theme
        theme_path = os.path.join(namespace.project_root, 'theme')

        if os.path.exists(theme_path):
            settings.THEME_PATHS.insert(0, theme_path)

        # output
        output_root = os.path.join(namespace.project_root, 'output')

        settings.OUTPUT_ROOT = output_root
        settings.MEDIA_ROOT = os.path.join(output_root, 'media')
        settings.STATIC_ROOT = os.path.join(output_root, 'static')

        # settings
        settings_path = os.path.join(namespace.project_root, 'settings.py')

        if os.path.exists(settings_path):
            settings.add(settings_path)

    # settings
    if namespace.settings:
        for module in namespace.settings:
            settings.add(module)

    # content
    if namespace.content_root:
        settings.CONTENT_ROOT = namespace.content_root

    if namespace.content_paths:
        settings.CONTENT_PATHS = namespace.content_paths

    return namespace, settings
