import re

from flamingo.core.parser import ContentParser

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={}">
  </head>
  <body></body>
</html>
"""


class RedirectRulesParser(ContentParser):
    FILE_EXTENSIONS = ['rr']
    RULE_RE = re.compile(r'^(?P<code>[0-9]+)(\s{1,})(?P<src>[^ ]+)(\s{1,})(?P<dst>[^ \n]+)$')  # NOQA

    def parse(self, file_content, content):
        content['output'] = '/dev/null'
        content['type'] = 'redirect-rules'
        content['rules'] = []

        for line in file_content.splitlines():
            if not line or line.startswith('#'):
                continue

            match = self.RULE_RE.search(line)

            if not match:
                continue

            match = match.groupdict()

            content['rules'].append(
                (match['code'], match['src'], match['dst'], )
            )


class Redirects:
    def parser_setup(self, context):
        context.parser.add_parser(RedirectRulesParser(context))

    def contents_parsed(self, context):
        rules = sum(
            context.contents.filter(type='redirect-rules').values('rules'), [])

        for status_code, source, destination in rules:
            if source.startswith('/'):
                source = source[1:]

            content = {
                'type': 'redirect-rule',
                'output': source,
                'content': HTML_TEMPLATE.format(destination),
            }

            context.contents.add(**content)
