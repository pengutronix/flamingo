from textwrap import dedent
from yaml import safe_load
import os

from flamingo.core.errors import FlamingoError


def plain_read(path):
    return open(path, 'r').read()


class ParsingError(FlamingoError):
    pass


class ContentParser:
    FILE_EXTENSIONS = []

    def __init__(self, context):
        self.context = context

    def parse_meta_data(self, file_content, content):
        if '\n\n\n' in file_content:
            content['content_offset'] = 2
            meta_data_string, markup_string = file_content.split('\n\n\n', 1)

        elif '\n\n' in file_content:
            content['content_offset'] = 1
            meta_data_string, markup_string = file_content.split('\n\n', 1)

        else:
            content['content_offset'] = 0

            return file_content

        try:
            meta = safe_load(meta_data_string)

            for key, value in meta.items():
                content[key] = value

            content['content_offset'] += len(meta_data_string.splitlines())

            return markup_string

        except Exception:
            content['content_offset'] = 0

            return file_content

    def parse(self, file_content, content):
        markup_string = self.parse_meta_data(file_content, content)

        content['content_body'] = markup_string.strip()


class FileParser:
    def __init__(self, context):
        self.context = context
        self._parsers = []

        if context.settings.USE_CHARDET:
            try:
                from flamingo.core.utils.chardet import chardet_read

                self.read = chardet_read

            except ImportError:
                context.logger.error(
                    'USE_CHARDET is set but chardet is not installed.'
                    'Falling back to plain python read')

                self.read = plain_read

        else:
            self.read = plain_read

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

        file_content = self.read(path)

        if self.context.settings.DEDENT_INPUT:
            file_content = dedent(file_content)

        parser.parse(file_content, content)
