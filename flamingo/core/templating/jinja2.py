import os

from jinja2 import Environment, FileSystemLoader, contextfunction

from flamingo.core.errors import ObjectDoesNotExist
from .base import TemplatingEngine


def silent_none(value):
    if value is None:
        return ''

    return value


@contextfunction
def link(context, path, name='', lang=''):
    i18n = 'flamingo.plugins.I18N' in context['context'].settings.PLUGINS

    try:
        content = context['context'].contents.get(path=path)

    except ObjectDoesNotExist:
        content = None

    if content and i18n:
        lang = lang or context['content']['lang']

        if content['lang'] != lang:
            content = context['context'].contents.get(id=content['id'],
                                                      lang=lang)

    if not content:
        content_path = context['content']['path']

        if not content_path and i18n and context['content']['translations']:
            content_path = context['content']['translations'].values('path')[0]

        context['context'].logger.error('%s: can not resolve link target ("%s", "%s")',  # NOQA
            content_path, path, name)

        return ''

    if not name:
        return content['url']

    return '<a href="{}">{}</a>'.format(content['url'], name)


class FlamingoEnvironment(Environment):
    def __init__(self, flamingo_context, *args, **kwargs):
        self.flamingo_context = flamingo_context

        super().__init__(*args, **kwargs)

    def get_template(self, *args, **kwargs):
        if args[0] == 'DEFAULT_TEMPLATE':
            return self.from_string('{{% extends "{}" %}}'.format(
                self.flamingo_context.settings.DEFAULT_TEMPLATE))

        return super().get_template(*args, **kwargs)


class Jinja2(TemplatingEngine):
    def __init__(self, context):
        super().__init__(context)

        self.env = FlamingoEnvironment(
            context,
            loader=FileSystemLoader(
                [os.path.join(i, 'templates') for i in self.theme_paths]),
            finalize=silent_none,
        )

        self.env.globals['link'] = link

    def render(self, template_name, template_context):
        return self.env.get_template(template_name).render(**template_context)

    def render_string(self, string, template_context):
        if not string or '{' not in string:
            return string

        template = self.env.from_string(string)

        return template.render(**template_context)
