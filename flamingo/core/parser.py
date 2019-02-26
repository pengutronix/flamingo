from configparser import ConfigParser, Error as ConfigParserError
import os

from flamingo.core.errors import FlamingoError


class ParsingError(FlamingoError):
    pass


class ContentParser:
    FILE_EXTENSIONS = []

    def __init__(self):
        self.configparser = ConfigParser(interpolation=None)

    def parse_meta_data(self, file_content, content):
        if '\n\n\n' in file_content:
            meta_data_string, markup_string = file_content.split('\n\n\n', 1)

        elif '\n\n' in file_content:
            meta_data_string, markup_string = file_content.split('\n\n', 1)

        else:
            return file_content

        try:
            self.configparser.clear()

            self.configparser.read_string(
                '[meta]\n{}'.format(meta_data_string))

            for option in self.configparser.options('meta'):
                content[option] = self.configparser.get('meta', option)

            return markup_string

        except ConfigParserError:
            return file_content

    def parse(self, file_content, content):
        markup_string = self.parse_meta_data(file_content, content)

        content['content_body'] = markup_string.strip()


class FileParser:
    def __init__(self):
        self._parsers = []

    def add_parser(self, parser):
        self._parsers.append(parser)

    def find_parser(self, extension):
        for parser in self._parsers:
            if extension in parser.FILE_EXTENSIONS:
                return parser

    def get_extensions(self):
        return sum([i.FILE_EXTENSIONS for i in self._parsers], [])

    def parse(self, path, content):
        extension = os.path.splitext(path)[1][1:]
        parser = self.find_parser(extension)

        if not parser:
            raise ParsingError(
                "file extension '{}' is not supported".format(extension))

        parser.parse(open(path, 'r').read(), content)  # FIXME: chardet
