import re

from docutils.parsers.rst import directives
from docutils.nodes import raw

from .base import NestedDirective


class Container(NestedDirective):
    def run(self):
        nodes = super().run()

        nodes.insert(0, raw('', '<div>', format='html'))
        nodes.append(raw('', '<div class="clearfix"></div></div>',
                         format='html'))

        return nodes


class BootstrapRow(NestedDirective):
    def run(self):
        nodes = super().run()

        nodes.insert(0, raw('', '<div class="row">', format='html'))
        nodes.append(raw('', '</div>', format='html'))

        return nodes


class BootstrapCol(NestedDirective):
    required_arguments = 1
    argument_re = re.compile(r'(xs|sm|md|lg)-([0-9]{1,2})')

    def parse_argument(self, argument):
        try:
            match = self.argument_re.search(argument)

            if match:
                aspect, size = match.groups()
                size = int(size)

                if 0 < size < 13:
                    return aspect, size

        except Exception:
            pass

        raise ValueError("'{}' is no valid Bootstrap3 col".format(argument))

    def run(self):
        nodes = super().run()
        aspect, size = self.parse_argument(self.arguments[0])

        nodes.insert(0, raw('', '<div class="col-{}-{}">'.format(aspect, size),
                            format='html'))

        nodes.append(raw('', '<div class="clearfix"></div></div>',
                         format='html'))

        return nodes


class Youtube(NestedDirective):
    has_content = False
    required_arguments = 1

    template = """
        <div class="embed-responsive embed-responsive-16by9">
            <iframe class="embed-responsive-item" src="{url}"></iframe>
        </div>
    """

    def run(self):
        url = 'https://www.youtube.com/embed/{}'.format(
            self.arguments[0].strip())

        return [
            raw('', self.template.format(url=url), format='html')
        ]


class Alert(NestedDirective):
    has_content = True
    required_arguments = 1

    def run(self):
        valid_alert_types = ('success', 'info', 'warning', 'danger', )
        alert_type = self.arguments[0].strip()

        if alert_type not in valid_alert_types:
            raise ValueError("'{}' is no valid alert type ({})".format(
                alert_type, ', '.join(valid_alert_types)))

        return [
            raw('', '<div class="alert alert-{}" role="alert">'.format(
                alert_type), format='html'),
            *super().run(),
            raw('', '</div>', format='html')
        ]


class rstBootstrap3:
    def parser_setup(self, context):
        directives.register_directive('div', Container)
        directives.register_directive('row', BootstrapRow)
        directives.register_directive('col', BootstrapCol)
        directives.register_directive('youtube', Youtube)
        directives.register_directive('alert', Alert)
