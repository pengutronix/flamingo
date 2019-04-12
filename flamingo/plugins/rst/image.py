from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from flamingo.core.plugins.media import add_media


def img(context):
    class Image(Directive):
        required_arguments = 1
        has_content = False

        def run(self):
            media = add_media(context, context.content, self.arguments[0])

            return [
                raw('', '<img src="{}">'.format(media['link']), format='html'),
            ]

    return Image


class rstImage:
    def parser_setup(self, context):
        directives.register_directive('img', img(context))
