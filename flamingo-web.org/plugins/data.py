from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight

from flamingo.plugins.rst.base import parse_rst


TEMPLATE = """
<div class="data">
    {highlight}
    <div class="description">
        {description}
    </div>
</div>
"""


def code_block(context):
    class Data(Directive):
        optional_arguments = 0
        has_content = True

        def run(self):
            python, description = (
                '\n'.join(self.content).split('\n\n', 1) + [''])[0:2]

            lexer = get_lexer_by_name('python')
            formatter = HtmlFormatter()
            html = highlight(python, lexer, formatter)

            return [
                raw('', TEMPLATE.format(highlight=html,
                                        description=parse_rst(description)),
                                        format='html'),
            ]

    return Data


class rstData:
    def parser_setup(self, context):
        directives.register_directive('data', code_block(context))
