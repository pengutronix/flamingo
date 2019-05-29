from io import StringIO
import logging
import re

from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import Directive
from docutils.utils import SystemMessage
from docutils.core import publish_parts
from docutils.nodes import raw

from flamingo.core.parser import ContentParser, ParsingError

SYSTEM_MESSAGE_RE = re.compile(r'^(?P<name>[^:]+):(?P<line>\d+): \((?P<level_name>[^/)]+)/(?P<level>\d+)\) (?P<short_description>[^\t\n]+)(?P<long_description>.*)?$', re.DOTALL)  # NOQA
logger = logging.getLogger('flamingo.plugins.rst.reStructuredText')


class reStructuredTextError(ParsingError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        for k, v in kwargs.items():
            setattr(self, k, v)


def parse_rst_parts(rst_input, system_message_re=SYSTEM_MESSAGE_RE,
                    logger=logger):

    if not isinstance(rst_input, str):
        rst_input = '\n'.join(rst_input)

    rst_error = None
    parsing_error = None

    settings_overrides = {
        'initial_header_level': '2',
        'traceback': True,
        'warning_stream': StringIO(),
        'embed_stylesheet': False,
        'dump_settings': False,
        'halt_level': 3,
    }

    try:
        return publish_parts(
            settings_overrides=settings_overrides,
            writer=Writer(),
            source=rst_input,
        )

    except SystemMessage as e:
        rst_error = e

    # parse docutils.utils.SystemMessage and re-raise SystemMessage
    # on parsing error
    try:
        result = system_message_re.search(rst_error.args[0])
        result = result.groupdict()

        result['level'] = int(result['level'])
        result['line'] = int(result['line'])

        if result['short_description'][-1] == '.':
            result['short_description'] = result['short_description'][:-1]

        if 'long_description' not in result:
            result['long_description'] = ''

    except Exception as e:
        parsing_error = e

        logger.error('%s raised while analyzing %s', parsing_error, rst_error,
                     exc_info=True)

    if parsing_error:
        raise rst_error

    raise reStructuredTextError(result['short_description'], **{
        'system_message': rst_error,
        **result,
    })


def parse_rst(*args, **kwargs):
    parts = parse_rst_parts(*args, **kwargs)
    html = ''

    if parts['html_title']:
        html += parts['html_title']

    if parts['html_subtitle']:
        html += parts['html_subtitle']

    html += parts['body']

    return html


class RSTParser(ContentParser):
    FILE_EXTENSIONS = ['rst']

    def parse(self, file_content, content):
        markup_string = self.parse_meta_data(file_content, content)
        parts = parse_rst_parts(markup_string)

        content['content_title'] = parts['title']
        content['content_body'] = ''

        if parts['html_subtitle']:
            content['content_body'] += parts['html_subtitle']

        content['content_body'] += parts['body']


class NestedDirective(Directive):
    has_content = True

    def run(self):
        content = parse_rst(self.content)

        return [
            raw('', content, format='html'),
        ]


class reStructuredText:
    def parser_setup(self, context):
        context.parser.add_parser(RSTParser(context))
