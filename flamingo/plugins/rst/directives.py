from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from flamingo.plugins.rst.parser import parse_rst


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


class Container(NestedDirective):
    option_spec = {
        'id': directives.unchanged,
        'style': directives.unchanged,
    }

    def run(self, context=None):
        html = self.parse_content(context)

        return [
            raw('', '<div>', format='html'),
            raw('', html, format='html'),
            raw('', '</div>', format='html'),
        ]
