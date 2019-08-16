import logging

from feedgen.feed import FeedGenerator

logger = logging.getLogger('flamingo.plugins.Feeds')


class Feeds:
    def pre_build(self, context):
        FEEDS_DOMAIN = getattr(context.settings, 'FEEDS_DOMAIN', '/')
        FEEDS = getattr(context.settings, 'FEEDS', [])

        for feed_config in FEEDS:
            try:
                content = {
                    'type': 'feed',
                    'feed_type': feed_config['type'],
                    'output': feed_config['output'],
                    'url': '/' + feed_config['output'],
                }

                if 'lang' in feed_config:
                    content['lang'] = feed_config['lang']

                fg = FeedGenerator()

                fg.id(feed_config['id'])
                fg.title(feed_config['title'])

                for i in feed_config['contents'](context):
                    fe = fg.add_entry()

                    # setup required entry attributes
                    fe_title = i['content_title']

                    fe_link = {
                        'href': '{}{}'.format(FEEDS_DOMAIN, i['url']),
                        'rel': 'alternate'
                    }

                    if 'entry-id' in feed_config:
                        fe_id = feed_config['entry-id'](i)

                    else:
                        fe_id = i['output']

                    if 'updated' in feed_config:
                        fe_updated = feed_config['updated'](i)

                    else:
                        fe_updated = ''

                    # check entry attributes
                    missing_attributes = []

                    if not fe_id:
                        missing_attributes.append('id')

                    if not fe_title:
                        missing_attributes.append('title')

                    if not fe_updated:
                        missing_attributes.append('updated')

                    if missing_attributes:
                        logger.error('%s is missing attributes: %s',
                                     i['path'] or i,
                                     ', '.join(missing_attributes))

                        return

                    # optional attributes
                    fe.id(fe_id)
                    fe.title(fe_title)
                    fe.updated(fe_updated)
                    fe.link(fe_link)

                    if i['content_body']:
                        fe.content(i['content_body'], type='html')

                    if i['authors']:
                        for author in i['authors']:
                            fe.author({
                                'name': author,
                            })

                    if i['summary']:
                        fe.summary(str(i['summary']))

                # generate output
                if feed_config['type'] == 'atom':
                    content['content_body'] = fg.atom_str().decode()

                elif feed_config['type'] == 'rss':
                    content['content_body'] = fg.rss_str().decode()

                context.contents.add(**content)

            except Exception:
                logger.error("feed '%s' setup failed", feed_config['id'],
                             exc_info=True)
