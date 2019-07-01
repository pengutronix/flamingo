from bs4 import BeautifulSoup

from flamingo.core.utils.html import extract_title, process_media_links
from flamingo.core.parser import ContentParser


class HTMLParser(ContentParser):
    FILE_EXTENSIONS = ['html']

    def parse(self, file_content, content):
        markup_string = self.parse_meta_data(file_content, content)
        soup = BeautifulSoup(markup_string, 'html.parser')

        raw_html = (
            self.context.settings.HTML_PARSER_RAW_HTML or
            bool(content['raw_html'])
        )

        if raw_html:
            content['content_title'] = ''
            content['content_body'] = markup_string

        else:
            title = extract_title(soup)
            process_media_links(self.context, content, soup)

            content['content_title'] = title
            content['content_body'] = str(soup)


class HTML:
    def parser_setup(self, context):
        context.parser.add_parser(HTMLParser(context))
