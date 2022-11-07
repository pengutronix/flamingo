from urllib.parse import urlparse
import os

from docutils.nodes import raw

from .utils import parse_role_text, parse_bool, register_canonical_role


class LinkRole:
    options = {}

    def __init__(self, context):
        self.context = context
        self.rst_base_plugin = context.plugins.get_plugin('reStructuredText')
        self.file_extensions = context.parser.get_extensions()

    def is_media_target(self, target):
        if os.path.splitext(target)[1][1:] in self.file_extensions:
            return False

        if target.startswith('/'):
            path = target[1:]

        else:
            path = os.path.join(
                os.path.dirname(self.context.content['path']),
                target,
            )

        path = os.path.join(
            self.context.settings.CONTENT_ROOT,
            os.path.normpath(path),
        )

        return os.path.exists(path)

    def __call__(self, name, rawtext, text, lineno, inliner):
        role_args = parse_role_text(text)
        options = role_args['options']

        if len(role_args['args']) == 1:
            target = role_args['args'][0]
            name = ''

        else:
            name, target = role_args['args']

        # handle external links
        result = urlparse(target)

        if result.scheme:
            if not name:
                name = target

            return [raw(
                '',
                '<a href="{}">{}</a>'.format(target, name),
                format='html')
            ], []

        # handle media files (downloads)
        if self.is_media_target(target):
            if not name:
                name = os.path.basename(target)

            media_content = self.context.add_media(target)

            return [raw(
                '',
                '<a href="{}">{}</a>'.format(media_content['url'], name),
                format='html')
            ], []

        # handle internal links
        abs_lineno = self.rst_base_plugin.offsets.get(
            self.context.content['path'], 0) + lineno

        if (not self.context.settings.PRE_RENDER_CONTENT or
           not self.context.content.get('is_template', True)):

            self.context.logger.error(
                '%s:%s: LinkError: internal links depend on content pre rendering which is disabled by your %s',  # NOQA
                self.context.content['path'],
                abs_lineno,
                ('settings'
                 if not self.context.settings.PRE_RENDER_CONTENT else
                 'content file'),
            )

        # add content path and lineno for better error reporting
        options['_content_path'] = self.context.content['path']
        options['_content_lineno'] = abs_lineno

        # generate html node
        if 'i18n' in options:
            options['i18n'] = parse_bool(options['i18n'])

        if not name:
            options['find_name'] = True

        return [raw(
            '',
            "{{{{ link(path='{}', name='{}', {}) }}}}".format(
                target,
                name,
                ', '.join([
                    "{}={}".format(k, repr(v))
                    for k, v in options.items()
                ])
            ),
            format='html',
        )], []


class rstLink:
    def parser_setup(self, context):
        register_canonical_role('link', LinkRole(context))
