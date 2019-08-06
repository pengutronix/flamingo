from feedgen.feed import FeedGenerator


class Feeds:
    def pre_build(self, context):
        FEEDS_DOMAIN = getattr(context.settings, 'FEEDS_DOMAIN', '/')
        FEEDS = getattr(context.settings, 'FEEDS', [])

        for feed_config in FEEDS:
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

                fe.title(i['content_title'])
                fe.content(i['content_body'], type='html')

                fe.link({
                    'href': '{}{}'.format(FEEDS_DOMAIN, i['url']),
                    'rel': 'alternate'
                })

                if 'entry-id' in feed_config:
                    fe.id(feed_config['entry-id'](i))

                else:
                    fe.id(i['output'])

                if 'updated' in feed_config:
                    updated = feed_config['updated'](i)

                    if updated:
                        fe.updated(updated)

                if i['authors']:
                    for author in i['authors']:
                        fe.author({
                            'name': author,
                        })

                if i['summary']:
                    fe.summary(str(i['summary']))

                if i['title']:
                    fe.title(i['title'])

            if feed_config['type'] == 'atom':
                content['content_body'] = fg.atom_str().decode()

            elif feed_config['type'] == 'rss':
                content['content_body'] = fg.rss_str().decode()

            context.contents.add(**content)
