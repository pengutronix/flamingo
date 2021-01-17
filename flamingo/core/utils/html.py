import re

from bs4 import BeautifulSoup

from flamingo.core.plugins.media import add_media

HEADING_RE = re.compile('^h[1-6]$')


class TitleNotFoundError(Exception):
    pass


def get_section_by_title(html, title, tag=None):
    soup = BeautifulSoup(html, 'html.parser')
    html = soup.find(name=tag or HEADING_RE, text=title)

    if not html:
        raise TitleNotFoundError

    return str(html.parent)


def extract_title(html):
    if isinstance(html, str):
        html = BeautifulSoup(html, 'html.parser')

    h1 = html.h1

    if h1:
        h1.extract()

        return h1.text

    return ''


def process_media_links(context, content, html):
    if isinstance(html, str):
        html = BeautifulSoup(html, 'html.parser')

    for img in html.find_all('img'):
        media_content = add_media(context, content, img['src'])
        img['src'] = media_content['url']
