import os

from bs4 import BeautifulSoup

import flamingo

PROJECT_NAME = 'flamingo'
CONTENT_ROOT = 'content'
OUTPUT_ROOT = 'output'
PRE_RENDER_CONTENT = False

THEME_PATHS = [
    'theme',
]

PLUGINS = [
    'flamingo.plugins.rstPygments',
    'flamingo.plugins.SimpleMenu',
    'flamingo.plugins.ReadTheDocs',
    'flamingo.plugins.Git',

    'plugins/data.py::rstData',
    'plugins/table.py::rstTable',
]

POST_BUILD_LAYERS = [
    'overlay',
]

MENU = [
    ['Documentation', [
        ['Basic Concepts', 'doc/basic_concepts.rst'],
        ['Installation', 'doc/installation.rst'],
        ['Settings', 'doc/settings.rst'],
        ['Data Model', 'doc/data_model.rst'],
        ['Writing Content', 'doc/writing_content.rst'],
        ['Writing Plugins and Hooks', 'doc/writing_plugins.rst'],
    ]],
    ['Plugins', [
        ['I18N', 'plugins/i18n.rst'],
        ['Layers', 'plugins/layers.rst'],
        ['Redirects', 'plugins/redirects.rst'],
        ['Tags', 'plugins/redirects.rst'],
        ['Authors', 'plugins/authors.rst'],
        ['Time', 'plugins/time.rst'],
    ]],
]


@flamingo.hook('contents_parsed')
def fix_documetation_links(context):
    for content in context.contents:
        if not content['content_body']:
            continue

        soup = BeautifulSoup(content['content_body'], 'html.parser')

        for link in soup.find_all('a'):
            if link['href'].startswith('flamingo-web.org/content/'):
                path, ext = os.path.splitext(
                    os.path.relpath(link['href'], 'flamingo-web.org/content/'))

                link['href'] = '/{}.html'.format(path)

                content['content_body'] = str(soup)


@flamingo.hook('contents_parsed')
def remove_badges_from_readme(context):
    readme = context.contents.get(path='index.rst')
    soup = BeautifulSoup(readme['content_body'], 'html.parser')

    for children in soup.children:
        if 'class' in children.attrs and 'section' in children.attrs['class']:
            break

        children.decompose()

    readme['content_body'] = str(soup)
