from copy import deepcopy
import logging
import os

from flamingo.core.errors import MultipleObjectsReturned, ObjectDoesNotExist
from flamingo.core.data_model import Content, Q
from flamingo.core.utils.string import slugify

logger = logging.getLogger('flamingo.plugins.Menu')


def is_active(section, menu, content):
    def _contains(menu, content):
        for i in menu:
            if i is content:
                return True

            if isinstance(i, (list, tuple, )):
                if _contains(i, content):
                    return True

        return False

    if isinstance(section, Section) and section.content is content:
        return True

    if (isinstance(section, Section) and
       isinstance(content['menu_path'], list) and
       section in content['menu_path']):

        return True

    if isinstance(menu, Content):
        return menu is content

    return _contains(menu, content)


def is_dict(v):
    return isinstance(v, dict)


def is_list(v):
    return isinstance(v, list)


class Section:
    def __init__(self, name, url=''):
        self.name = name
        self.url = url or slugify(self.name)
        self.content = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Section('{}', url='{}')>".format(self.name, self.url)


class Menu:
    THEME_PATHS = [
        os.path.join(os.path.dirname(__file__), 'theme'),
    ]

    def templating_engine_setup(self, context, templating_engine):
        templating_engine.env.globals['is_active'] = is_active
        templating_engine.env.globals['is_dict'] = is_dict
        templating_engine.env.globals['is_list'] = is_list

    def contents_parsed(self, context):
        create_indices = context.settings.get('MENU_CREATE_INDICES', False)

        index_template = context.settings.get(
            'MENU_INDEX_TEMPLATE', 'menu/index.html')

        if not hasattr(context.settings, 'MENU'):
            context.settings.MENU = {
                'main': [],
            }

        self.menu = deepcopy(context.settings.MENU)

        def resolve_links(menu):
            for item in menu:
                section_args, url = item

                if isinstance(url, list):
                    # setup section
                    if not isinstance(section_args, (list, tuple)):
                        section_args = [section_args]

                    if not isinstance(item[0], Section):
                        item[0] = Section(*section_args)

                    resolve_links(url)

                else:
                    logger.debug('resolving %s', item[1])

                    try:
                        if isinstance(item[1], (Content, Section, )):
                            logger.debug('resolving skipped')

                            return

                        if isinstance(item[1], str):
                            lookup = Q(path=item[1])

                        elif not isinstance(item[1], Q):
                            lookup = Q(item[1])

                        else:
                            lookup = item[1]

                        item[1] = context.contents.get(lookup)

                        logger.debug('%s -> %s', lookup, item[1])

                    except ObjectDoesNotExist:
                        logger.error(
                            "no content with %s %s found",
                            'path' if isinstance(lookup, str) else 'lookup',
                            lookup or repr(lookup),
                        )

                    except MultipleObjectsReturned:
                        logger.error(
                            "multiple contents found with %s %s found",
                            'path' if isinstance(lookup, str) else 'lookup',
                            lookup or repr(lookup),
                        )

        # setup menus
        if isinstance(self.menu, list):
            self.menu = {
                'main': self.menu,
            }

        elif 'main' not in self.menu:
            self.menu['main'] = []

        # resolve links
        for menu_name, menu in self.menu.items():
            resolve_links(menu)

        # create section indices
        def create_section_indices(menu, path):
            current_section = None

            def gen_content(menu, path):
                url = '/'

                for section in path + [current_section]:
                    url = os.path.join(url, section.url)

                url = os.path.join(url, 'index.html')

                content = Content(
                    type='menu/index',
                    title=current_section.name,
                    url=url,
                    output=url[1:],
                    menu=menu,
                    template=index_template,
                    menu_path=path,
                )

                context.contents.add(content)
                current_section.content = content

            for item in menu:
                if isinstance(item, Section):
                    current_section = item

                    gen_content(menu[1:], path)

                elif isinstance(item, Content):
                    item['menu_path'] = path

                elif isinstance(item, (list, tuple)):
                    if current_section:
                        create_section_indices(item, path+[current_section])

                    else:
                        create_section_indices(item, path)

        if create_indices:
            for menu_name, menu in self.menu.items():
                create_section_indices(menu, path=[])
