from argparse import ArgumentParser, RawTextHelpFormatter
import subprocess
import logging

try:
    import coloredlogs

    COLOREDLOGS = True

except ImportError:  # pragma: no cover
    COLOREDLOGS = False

from flamingo.core.settings import Settings
import flamingo

logger = logging.getLogger('flamingo')

VERSION = 'v{}'.format(flamingo.VERSION_STRING)
DESCRIPTION_HEADER = r"""
  _        __ _                 _
 ^-)      / _| |               (_)
  (.._   | |_| | __ _ _ __ ___  _ _ __   __ _  ___
   \`\\  |  _| |/ _` | '_ ` _ \| | '_ \ / _` |/ _ \
    |>   | | | | (_| | | | | | | | | | | (_| | (_) |
   /|    |_| |_|\__,_|_| |_| |_|_|_| |_|\__, |\___/
                                         __/ |
{}{} |___/

  https://github.com/pengutronix/flamingo

""".format(' ' * (39 - len(VERSION)), VERSION)


class LogFilter:
    def __init__(self, names):
        self.names = names

    def filter(self, record):
        return record.name in self.names


def color(string, color='', background='', style='', reset=True):
    reset_string = '\033[00m' if reset else ''

    if not string and reset:
        return reset_string

    if style:
        style = {
            'bright': '1',
            'underlined': '2',
            'negative': '3',
        }[style]

    if color:
        color = {
            'black': '30',
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37',
        }[color]

        if style:
            color = ';{}'.format(color)

    if background:
        background = {
            'black': '40',
            'red': '41',
            'green': '42',
            'yellow': '43',
            'blue': '44',
            'magenta': '45',
            'cyan': '46',
            'white': '47',
        }[background]

        if color:
            background = ';{}'.format(background)

    return '\033[{}{}{}m{}{}'.format(
        style,
        color,
        background,
        string,
        reset_string,
    )


def success(string):
    return color(string, color='green')


def warning(string):
    return color(string, color='yellow')


def error(string):
    return color(string, color='red', style='bright')


def critical(string):
    return color(string, color='white', background='red', style='bright')


def get_raw_parser(*parser_args, description='', **parser_kwargs):
    description = '{}\n{}'.format(DESCRIPTION_HEADER, description)

    parser = ArgumentParser(*parser_args, description=description,
                            formatter_class=RawTextHelpFormatter,
                            **parser_kwargs)
    parser.add_argument('--version', action='version', version=VERSION)

    return parser


def gen_default_parser(*parser_args, description='', **parser_kwargs):

    parser = get_raw_parser(*parser_args, description=description,
                            **parser_kwargs)

    parser.add_argument('-s', '--settings', nargs='+')
    parser.add_argument('-c', '--content-root', type=str)
    parser.add_argument('--content-paths', type=str, nargs='+')

    parser.add_argument(
        '-l', '--log-level',
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
        default='WARN',
    )

    parser.add_argument('--loggers', type=str, nargs='+')
    parser.add_argument('-d', '--debug', action='store_true')

    return parser


def parse_args(parser=None, setup_logging=True):
    parser = parser or gen_default_parser()
    namespace = parser.parse_args()
    settings = Settings()

    # loglevel / debug mode
    if setup_logging:
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

        if COLOREDLOGS:  # pragma: no cover
            coloredlogs.install(level=log_level)

        if namespace.loggers:
            logging.root.handlers[0].addFilter(LogFilter(namespace.loggers))

    # settings
    if namespace.settings:
        for module in namespace.settings:
            try:
                settings.add(module)

            except ImportError:
                exit('import error: {}'.format(module))

    # content
    if namespace.content_root:
        settings.CONTENT_ROOT = namespace.content_root

    if namespace.content_paths:
        settings.CONTENT_PATHS = namespace.content_paths

    return namespace, settings


def start_editor(path):
    command = ["""
        $((test -n "$EDITOR" && echo $EDITOR) || which vim || which nano) {}
    """.format(path)]

    subprocess.run(command, shell=True, executable='/bin/bash')
