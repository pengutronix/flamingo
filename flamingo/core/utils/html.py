from bs4 import BeautifulSoup


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
