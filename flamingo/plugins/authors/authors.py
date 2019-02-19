import os

from flamingo.core.utils.string import split, slugify


class Authors:
    THEME_PATHS = [os.path.join(os.path.dirname(__file__), 'theme')]

    def contents_parsed(self, context):
        content_key = getattr(context.settings, 'I18N_CONTENT_KEY', 'id')

        for content in context.contents:
            if content['authors']:
                content['authors'] = split(content['authors'])

            else:
                content['authors'] = []

        authors = sorted(
            list(set(sum(context.contents.values('authors'), []))))

        # gen author pages
        for author in authors:
            output = os.path.join('authors/{}.html'.format(slugify(author)))

            context.contents.add(**{
                content_key: '_author/{}'.format(author),
                'output': output,
                'url': '/' + output,
                'author': author,
                'template': 'author.html',
            })
