from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from .base import parse_rst


def file(context):
    class File(Directive):
        required_arguments = 1
        has_content = True

        def run(self):
            filename = self.arguments[0]
            _, _, link = context.copy_media(filename,
                                            context.content['path'])

            content = parse_rst(self.content)

            return [
                raw('', '<a href="{}">{}</a>'.format(link, content),
                    format='html'),
            ]

    return File


class rstFile:
    def parser_setup(self, context):
        directives.register_directive('file', file(context))
