import logging

from docutils.nodes import system_message

from flamingo.plugins.rst.parser import parse_rst_parts
from flamingo.plugins.rst.directives import Container
from flamingo.plugins.rst import register_directive
from flamingo.core.parser import ContentParser


logger = logging.getLogger('flamingo.plugins.reStructuredText')


class RSTParser(ContentParser):
    FILE_EXTENSIONS = ['rst']

    def parse(self, file_content, content):
        plugin = self.context.plugins.get_plugin('reStructuredText')
        path = content['path']

        try:
            markup_string = self.parse_meta_data(file_content, content)
            parts = parse_rst_parts(markup_string, self.context)

            content['content_title'] = parts['title']
            content['content_body'] = ''

            if parts['html_subtitle']:
                content['content_body'] += parts['html_subtitle']

            content['content_body'] += parts['body']

        finally:
            if path in plugin.offsets:
                plugin.offsets.pop(path)


class reStructuredText:
    def setup(self, context):
        logger.debug('reset offsets')

        self.offsets = {}

    def parser_setup(self, context):
        context.parser.add_parser(RSTParser(context))

        class _Container(Container):
            def run(self):
                return super().run(context=context)

        register_directive('div', _Container)

    def rst_document_parsed(self, context, document):
        """
        This hook removes all docutils system messages from docutils documents
        """

        if (not context.settings.get(
               'RST_REMOVE_SYSTEM_MESSAGES_FROM_OUPUT', True)):

            return

        logger.debug('%s: removing system messages', context.content['path'])

        removed = [0]

        def remove_system_messages(children, removed):
            for child in children[::]:
                if isinstance(child, system_message):
                    children.remove(child)
                    removed[0] += 1

                elif (hasattr(child, 'attributes') and
                      'classes' in child.attributes and
                      'system-messages' in child.attributes['classes']):

                    children.remove(child)
                    removed[0] += 1

                elif child.children:
                    remove_system_messages(child.children, removed)

        remove_system_messages(document.children, removed)

        logger.debug('%s: %s system messages removed',
                     context.content['path'], removed[0])
