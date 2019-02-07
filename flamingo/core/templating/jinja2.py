import os

from jinja2 import Environment, FileSystemLoader, contextfunction

from .base import TemplatingEngine


def silent_none(value):
    if value is None:
        return ''

    return value


@contextfunction
def render(context, template_string):
    if not template_string:
        return ''

    if '{' not in template_string:
        return template_string

    template = context['context'].templating_engine.env.from_string(
        template_string)

    return template.render(**context)


@contextfunction
def link(context, path, name='', lang=''):
    content = context['context'].contents.get(path=path)
    i18n = 'flamingo.plugins.I18N' in context['context'].settings.PLUGINS

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


class Jinja2(TemplatingEngine):
    def __init__(self, theme_paths):
        if not isinstance(theme_paths, list):
            theme_paths = [theme_paths]

        self.theme_paths = theme_paths

        self.env = Environment(
            loader=FileSystemLoader(
                [os.path.join(i, 'templates') for i in theme_paths]),
            finalize=silent_none,
        )

        self.env.globals['render'] = render
        self.env.globals['link'] = link

    def render(self, template_name, template_context):
        return self.env.get_template(template_name).render(**template_context)
