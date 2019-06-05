from textwrap import dedent
import os
import re

from yaml import safe_load

from flamingo.core.errors import FlamingoError

NO_META_DATA_RE = re.compile(r'^((\s+)?\n){2,}')
DELIMITER_RE = re.compile(r'((\s+)?\n){3,}')


def plain_read(path):
    return open(path, 'r').read()


class ParsingError(FlamingoError):
    pass


class ContentParser:
    FILE_EXTENSIONS = []

    def __init__(self, context):
        self.context = context

    def parse_meta_data(self, file_content, content):
        def raise_yaml_parsing_error():
            markup_string_end = len(meta_data_string.splitlines()) + 1

            raise ParsingError(
                'Invalid meta data at line 1 to {}. '
                'Meta data has to be valid YAML, defining a key value store'
                ''.format(markup_string_end)
            )

        # check for meta data
        match = NO_META_DATA_RE.search(file_content)

        if match:
            content['content_offset'] = 0

            return file_content

        # find delimter
        match = DELIMITER_RE.search(file_content)

        if not match:
            raise ParsingError(
                'Invalid format. Content files have to start with two blank '
                'lines, or a meta data block followed by two blank lines and '
                'a markup block'
            )

        delimiter_start, delimiter_end = match.span()

        # split file_content
        delimter = file_content[delimiter_start:delimiter_end]
        meta_data_string = file_content[:delimiter_start]
        markup_string = file_content[delimiter_end:]

        content['content_offset'] = (len(meta_data_string.splitlines()) +
                                     len(delimter.splitlines()) - 1)

        # parse meta data
        try:
            meta = safe_load(meta_data_string)

        except Exception:
            raise_yaml_parsing_error()

        if meta:
            if not isinstance(meta, dict):
                raise_yaml_parsing_error()

            for key, value in meta.items():
                content[key] = value

        else:
            content['content_offset'] += 1

        return markup_string

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
