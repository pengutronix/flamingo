import logging

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from bs4 import BeautifulSoup

from flamingo.core.utils.html import get_section_by_title, TitleNotFoundError
from flamingo.plugins.rst import register_directive, parse_rst
from flamingo.core.errors import ObjectDoesNotExist


logger = logging.getLogger('flamingo.plugins.rst.parser.include')


def get_section(html, id):
    soup = BeautifulSoup(html, 'html.parser')

    html = soup.find(**{
        'name': 'div',
        'class': 'section',
        'id': id,
    })

    if html:
        return str(html)

    return ''


def generate_directives(context):
    rst_base_plugin = context.plugins.get_plugin('reStructuredText')

    class Section(Directive):
        required_arguments = 1
        has_content = True

        def run(self):
            content = '<div class="section" id="{}">{}</div>'.format(
                self.arguments[0],
                parse_rst(self.content, context)
            )

            return [
                raw('', content, format='html'),
            ]

    class Include(Directive):
        has_content = False
        required_arguments = 1

        option_spec = {
            'title': directives.unchanged,
            'section': directives.unchanged,
        }

        def run(self):
            # find current lineno
            lineno = self.lineno + rst_base_plugin.offsets.get(
                context.content['path'], 0)

            # find content
            path = self.arguments[0]

            if not path.startswith('/'):
                logger.error(
                    "%s:%s includes have to be absolute",
                    context.content['path'],
                    lineno,
                )

                return []

            try:
                content = context.contents.get(path=path[1:])

            except ObjectDoesNotExist:
                logger.error(
                    "%s:%s content '%s' does not exist",
                    context.content['path'],
                    lineno,
                    path,
                )

                return []

            # mark included content as dependency for the current content
            if not context.content['related_paths']:
                context.content['related_paths'] = []

            context.content['related_paths'].append(content['path'])

            # parse included content if content_body is present yet
            if not content['content_body']:
                context.parse(content)

            # check arguments
            if ('section' in self.options and
               'title' in self.options):

                logger.error(
                    "%s:%s has no ambiguous arguments",
                    context.content['path'],
                    lineno,
                )

                return []

            # include full document
            if self.options == {}:
                return [
                    raw('', content['content_body'], format='html'),
                ]

            # include html by section id
            if 'section' in self.options:
                section_id = self.options['section']

                html = get_section(
                    content['content_body'],
                    section_id,
                )

                if not html:
                    logger.error(
                        "%s:%s '%s' has no section with id '%s'",
                        context.content['path'],
                        lineno,
                        path,
                        section_id,
                    )

                    return []

                return [
                    raw('', html, format='html'),
                ]

            # extract html by title
            elif 'title' in self.options:
                title = self.options['title'].strip()

                try:
                    html = get_section_by_title(content['content_body'], title)

                except TitleNotFoundError:
                    logger.error(
                        "%s:%s '%s' has no headline '%s'",
                        context.content['path'],
                        lineno,
                        path,
                        title,
                    )

                    return []

            return [
                raw('', html, format='html'),
            ]

    return Section, Include


class rstInclude:
    def parser_setup(self, context):
        Section, Include = generate_directives(context)

        register_directive('section', Section)
        register_directive('include', Include)
