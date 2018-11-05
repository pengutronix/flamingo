from configparser import ConfigParser, Error as ConfigParserError
from io import StringIO
import os

from flamingo.core.errors import FlamingoError


class ParsingError(FlamingoError):
    pass


class ContentParser:
    FILE_EXTENSIONS = []

    def __init__(self):
        self.configparser = ConfigParser(interpolation=None)

    def parse_meta_data(self, fp):
        meta_data_buffer = StringIO('[meta]\n')
        meta_data_buffer.read()

        empty_lines = 0

        while True:
            line = fp.readline()

            if not line:  # eof
                break

            if not line.strip():
                empty_lines += 1

            else:
                empty_lines = 0

            if empty_lines == 2:
                break

            meta_data_buffer.write(line)

        meta_data_buffer.seek(0)

        self.configparser.clear()
        self.configparser.read_file(meta_data_buffer)

        meta = {k: self.configparser.get('meta', k)
                for k in self.configparser.options('meta')}

        return meta

    def parse_content(self, fp):
        return fp.read().strip()

    def parse(self, fp):
        meta = self.parse_meta_data(fp)
        content = self.parse_content(fp)

        return meta, content


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

    def parse(self, path):
        extension = os.path.splitext(path)[1][1:]
        parser = self.find_parser(extension)

        if not parser:
            raise ParsingError(
                "file extension '{}' is not supported".format(extension))

        try:
            return parser.parse(open(path, 'r'))  # FIXME: chardet

        except ConfigParserError:
            raise ParsingError('Metadata seem to be broken')
