from flamingo.core.parser import ContentParser


class INIParser(ContentParser):
    FILE_EXTENSIONS = ['ini']

    """
    This parser can be used to load files that do not contain a content part
    and only contain a metadata part.
    This can be useful if you want to generate pages just from some
    pice of structured information and all your markup is handled in
    the template.

    Add *.meta -files to your content-directory to use this parser.
    """

    def parse(self, file_content, content):

        # .meta files do not have a content part.
        # But parse_meta_data() assumes it has one.
        # We will add an extra \n\n\n at the end to make it useable for our
        # usecase. We will discard the body anway.

        file_content = file_content + "\n\n\n"

        self.parse_meta_data(file_content, content)


class INI:
    def parser_setup(self, context):
        context.parser.add_parser(INIParser(context))
