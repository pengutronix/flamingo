import os
from copy import copy

from flamingo.core.data_model import Q

INDEX_PAGE = """
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url=/{}/">
  </head>
  <body></body>
</html>
"""


class I18N:
    def contents_parsed(self, context):
        # settings
        content_key = getattr(context.settings, 'I18N_CONTENT_KEY', 'id')
        languages = getattr(context.settings, 'I18N_LANGUAGES', ['en', 'de'])

        default_language = getattr(context.settings, 'I18N_DEFAULT_LANGUAGE',
                                   'en')

        enforce_redirect = getattr(context.settings, 'I18N_ENFORCE_REDIRECT',
                                   True)

        ignore = getattr(context.settings, 'I18N_IGNORE',
                         {'i18n_ignore__isnull': False})

        for content in context.contents.exclude(ignore):
            # set lang tag if not set
            if not content['lang']:
                content['lang'] = default_language

            # if no content_key is set the path becomes the content_key
            if not content[content_key]:
                content[content_key] = content['path']

            # find translations
            translation_langs = context.contents.filter(
                **{content_key: content[content_key]}).values('lang')

            # add missings translations
            for l in languages:
                if l not in translation_langs:
                    content_data = copy(content.data)

                    if 'path' in content_data:
                        content_data['i18n_path'] = content_data['path']
                        del content_data['path']

                    content_data['lang'] = l

                    context.contents.add(**content_data)

        # set output and url according to lang code
        # set translations
        for content in context.contents.exclude(ignore):
            content['output'] = os.path.join(content['lang'],
                                             content['output'])

            content['url'] = os.path.join('/', content['lang'],
                                          content['url'][1:])

            content['translations'] = context.contents.filter(
                Q(**{content_key: content[content_key]}),
                ~Q(lang=content['lang']),
            )

        # enforce redirect
        if enforce_redirect:
            context.contents.add(**{
                'output': 'index.html',
                'url': '/',
                'content_body': INDEX_PAGE.format(default_language),
            })
