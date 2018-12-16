from io import StringIO

from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import Directive
from docutils.core import publish_parts
from docutils.nodes import raw

from flamingo.core.parser import ContentParser


def parse_rst_parts(rst_input):
    if not isinstance(rst_input, str):
        rst_input = '\n'.join(rst_input)

    settings_overrides = {
        'initial_header_level': '2',
        'traceback': True,
        'warning_stream': StringIO(),
        'embed_stylesheet': False,
    }

    return publish_parts(
        settings_overrides=settings_overrides,
        writer=Writer(),
        source=rst_input,
    )


def parse_rst(rst_input):
    parts = parse_rst_parts(rst_input)
    html_output = ''

    if parts['title']:
        html_output += '<h1>{}</h1>'.format(parts['title'])

    html_output += parts['body']

    return html_output


class RSTParser(ContentParser):
    FILE_EXTENSIONS = ['rst']

    def parse(self, fp, content):
        self.parse_meta_data(fp, content)

        parts = parse_rst_parts(fp.read())

        content['content_body'] = parts['body']
        content['content_title'] = parts['title']


class NestedDirective(Directive):
    has_content = True

    def run(self):
        content = parse_rst(self.content)

        return [
            raw('', content, format='html'),
        ]


class reStructuredText:
    def parser_setup(self, context):
        context.parser.add_parser(RSTParser())
