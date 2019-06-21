from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from pygments import highlight


def code_block(context):
    class CodeBlock(Directive):
        optional_arguments = 1
        has_content = True

        def run(self):
            try:
                if self.arguments:
                    lexer = get_lexer_by_name(self.arguments[0])

                else:
                    lexer = guess_lexer('\n'.join(self.content))

            except (ClassNotFound, IndexError):
                lexer = get_lexer_by_name('text')

            formatter = HtmlFormatter()
            html = highlight('\n'.join(self.content), lexer, formatter)

            return [
                raw('', html, format='html'),
            ]

    return CodeBlock


class rstPygments:
    def parser_setup(self, context):
        directives.register_directive('code-block', code_block(context))
