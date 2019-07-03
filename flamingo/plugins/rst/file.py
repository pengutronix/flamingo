from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from flamingo.core.plugins.media import add_media


def file(context):
    class File(Directive):
        required_arguments = 1
        has_content = True

        def run(self):
            media = add_media(context, context.content, self.arguments[0])

            return [
                raw('', '<a href="{}">{}</a>'.format(
                        media['link'], ' '.join(self.content).strip()),
                    format='html'),
            ]

    return File


class rstFile:
    def parser_setup(self, context):
        directives.register_directive('file', file(context))
