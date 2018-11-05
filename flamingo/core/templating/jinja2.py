import os

from jinja2 import Environment, FileSystemLoader

from .base import TemplatingEngine


def silent_none(value):
    if value is None:
        return ''

    return value


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

    def render(self, template_name, template_context):
        return self.env.get_template(template_name).render(**template_context)
