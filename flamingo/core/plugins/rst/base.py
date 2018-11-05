from docutils.writers.html4css1 import Writer
from docutils.parsers.rst import Directive
from docutils.core import publish_parts
from docutils.nodes import raw

from flamingo.core.parser import ContentParser


def parse_rst(rst_input):
    if not isinstance(rst_input, str):
        rst_input = '\n'.join(rst_input)

    parts = publish_parts(writer=Writer(), source=rst_input)
    html_output = ''

    if parts['title']:
        html_output += '<h1>{}</h1>'.format(parts['title'])

    html_output += parts['body']

    return html_output


class RSTParser(ContentParser):
    FILE_EXTENSIONS = ['rst']

    def parse_content(self, fp):
        return parse_rst(fp.read())


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
