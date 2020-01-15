import logging
import re

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw, system_message
from docutils.writers.html4css1 import Writer
from docutils.utils import SystemMessage
from docutils.core import publish_parts

from flamingo.core.parser import ContentParser, ParsingError

SYSTEM_MESSAGE_RE = re.compile(r'^(?P<name>[^:]+):(?P<line>\d+): \((?P<level_name>[^/)]+)/(?P<level>\d+)\) (?P<short_description>[^\t\n]+)(?P<long_description>.*)?$', re.DOTALL)  # NOQA
logger = logging.getLogger('flamingo.plugins.reStructuredText')


class reStructuredTextError(ParsingError):
    def __init__(self, *args, name=None, line=None, level_name=None,
                 level=None, short_description=None, long_description=None,
                 **kwargs):

        super().__init__(*args)

        self.name = name
        self.line = line
        self.level_name = level_name
        self.level = level
        self.short_description = short_description
        self.long_description = long_description


def parse_system_message(raw_message, system_message_re=SYSTEM_MESSAGE_RE):
    """
    takes a docutils.utils.SystemMessage object or a docutils SystemMessage
    as string

    returns: {
        'name': <str>,
        'line': <int>,
        'short_description': <str>,
        'long_description': <str>,
        'system_message': <docutils.utils.SystemMessage>,
    }

    """

    try:
        message = raw_message

        if isinstance(message, Exception):
            logger.debug(message, exc_info=True)
            message = message.args[0]

        # parse message
        result = system_message_re.search(message)
        result = result.groupdict()

        result['level'] = int(result['level'])
        result['line'] = int(result['line'])

        if result['short_description'][-1] == '.':
            result['short_description'] = result['short_description'][:-1]

        if 'long_description' not in result:
            result['long_description'] = ''

        result['system_message'] = raw_message

        return result

    except Exception:
        logger.error('exception occoured while parsing %s',
                     raw_message, exc_info=True)

        raise


class WarningStream:
    def __init__(self, context):
        self.context = context

    def write(self, warning):
        plugin = self.context.plugins.get_plugin('reStructuredText')
        path = self.context.content['path']
        offset = plugin.offsets.get(path, 0)

        message = parse_system_message(warning)

        level_name = message['level_name'].strip().upper()
        path = self.context.content['path']
        short_description = message['short_description'].strip()
        line = message['line'] + offset

        if level_name == 'DEBUG':
            self.context.logger.debug(
                '%s:%s: %s', path, line, short_description)

        elif level_name == 'INFO':
            self.context.logger.info(
                '%s:%s: %s', path, line, short_description)

        elif level_name == 'WARNING':
            self.context.logger.warning(
                '%s:%s: %s', path, line, short_description)


class SilentWriter(Writer):
    """
    This writer subclass removes all SystemMessages from its doctree
    """

    def write(self, document, destination):
        def remove_system_messages(children):
            for child in children[::]:
                if isinstance(child, system_message):
                    children.remove(child)

                elif child.children:
                    remove_system_messages(child.children)

        remove_system_messages(document.children)

        return super().write(document, destination)


_silent_writer = SilentWriter()


def parse_rst_parts(rst_input, context, system_message_re=SYSTEM_MESSAGE_RE):
    # setup offset
    plugin = context.plugins.get_plugin('reStructuredText')
    path = context.content['path']

    if path not in plugin.offsets:
        plugin.offsets[path] = context.content.get('content_offset', 0)

    # parse rst
    if not isinstance(rst_input, str):
        rst_input = '\n'.join(rst_input)

    rst_error = None
    parsing_error = None

    settings_overrides = {
        'initial_header_level': '2',
        'traceback': True,
        'warning_stream': WarningStream(context),
        'embed_stylesheet': False,
        'dump_settings': False,
        'halt_level': 3,
        'report_level': 1,

        **context.settings.get('RST_SETTINGS_OVERRIDES', {}),
    }

    try:
        output = publish_parts(
            settings_overrides=settings_overrides,
            writer=_silent_writer,
            source=rst_input,
        )

        return output

    except SystemMessage as e:
        rst_error = e

    # parse docutils.utils.SystemMessage and re-raise SystemMessage
    # on parsing error
    try:
        message = parse_system_message(rst_error)
        message['line'] += plugin.offsets[path]

    except Exception as e:
        parsing_error = e

    if parsing_error:
        raise rst_error

    raise reStructuredTextError(message['short_description'], **message,)


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
        plugin = self.context.plugins.get_plugin('reStructuredText')
        path = content['path']

        try:
            markup_string = self.parse_meta_data(file_content, content)
            parts = parse_rst_parts(markup_string, self.context)

            content['content_title'] = parts['title']
            content['content_body'] = ''

            if parts['html_subtitle']:
                content['content_body'] += parts['html_subtitle']

            content['content_body'] += parts['body']

        finally:
            if path in plugin.offsets:
                plugin.offsets.pop(path)


class NestedDirective(Directive):
    has_content = True

    def parse_content(self, context):
        plugin = context.plugins.get_plugin('reStructuredText')
        path = context.content['path']

        try:
            plugin.offsets[path] += self.content_offset

            return parse_rst(self.content, context)

        finally:
            plugin.offsets[path] -= self.content_offset

    def run(self, context=None):
        return [
            raw('', self.parse_content(context), format='html'),
        ]


def _container(context):
    class Container(NestedDirective):
        option_spec = {
            'id': directives.unchanged,
            'style': directives.unchanged,
        }

        def run(self):
            html = self.parse_content(context)

            return [
                raw('', '<div>', format='html'),
                raw('', html, format='html'),
                raw('', '</div>', format='html'),
            ]

    return Container


class reStructuredText:
    def setup(self, context):
        logger.debug('reset offsets')

        self.offsets = {}

    def parser_setup(self, context):
        context.parser.add_parser(RSTParser(context))
        directives.register_directive('div', _container(context))
