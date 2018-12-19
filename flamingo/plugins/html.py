from flamingo.core.parser import ContentParser


class HTMLParser(ContentParser):
    FILE_EXTENSIONS = ['html']


class HTML:
    def parser_setup(self, context):
        context.parser.add_parser(HTMLParser())
