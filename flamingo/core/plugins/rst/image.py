from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw


def img(context):
    class Image(Directive):
        required_arguments = 1
        has_content = False

        def run(self):
            filename = self.arguments[0]
            _, _, link = context.copy_media(filename,
                                            context.content_data['path'])

            return [
                raw('', '<img src="{}">'.format(link), format='html'),
            ]

    return Image


class rstImage:
    def parser_setup(self, context):
        directives.register_directive('img', img(context))
