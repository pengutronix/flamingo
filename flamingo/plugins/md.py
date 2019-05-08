from bs4 import BeautifulSoup
import markdown

from flamingo.core.utils.html import extract_title, process_media_links
from flamingo.core.parser import ContentParser


class MarkdownParser(ContentParser):
    FILE_EXTENSIONS = ['md']

    def parse(self, file_content, content):
        markup_string = self.parse_meta_data(file_content, content)
        html = markdown.markdown(markup_string)
        soup = BeautifulSoup(html, 'html.parser')

        title = extract_title(soup)
        process_media_links(self.context, content, soup)

        content['content_title'] = title
        content['content_body'] = str(soup)


class Markdown:
    def parser_setup(self, context):
        context.parser.add_parser(MarkdownParser(context))
