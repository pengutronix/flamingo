from bs4 import BeautifulSoup


class TitleNotFoundError(Exception):
    pass


def extract_section_by_title(html, title, tag='h2'):
    soup = BeautifulSoup(html, 'html.parser')
    html = soup.find(name=tag, text=title)

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
        _, _, link = context.copy_media(img['src'], content['path'])
        img['src'] = link
