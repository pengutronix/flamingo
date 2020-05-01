import os

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from pygments import highlight

from flamingo.plugins.rst import register_directive


def code_block(context):
    class CodeBlock(Directive):
        optional_arguments = 1
        has_content = True

        option_spec = {
            'license': directives.unchanged,
            'template': directives.unchanged,
            'include': directives.unchanged,
        }

        def run(self):
            content = ''

            if self.content:
                content += '\n'.join(self.content)

            if 'include' in self.options:
                if content:
                    content += '\n'

                path = os.path.join(
                    os.path.dirname(context.content['path']),
                    self.options['include'],
                )

                content += open(path, 'r').read()

            try:
                if self.arguments:
                    lexer = get_lexer_by_name(self.arguments[0])

                else:
                    lexer = guess_lexer(content)

            except (ClassNotFound, IndexError):
                lexer = get_lexer_by_name('text')

            formatter = HtmlFormatter()
            content = highlight(content, lexer, formatter)

            # find template
            template = self.options.get(
                'template', context.settings.DEFAULT_CODE_BLOCK_TEMPLATE)

            node_content = context.templating_engine.render(
                template,
                {
                    'context': context,
                    'content': content,
                    'license': self.options.get('license', ''),
                },
                handle_exceptions=False,
            )

            return [
                raw('', node_content, format='html')
            ]

    return CodeBlock


class rstPygments:
    def parser_setup(self, context):
        register_directive('code-block', code_block(context))
