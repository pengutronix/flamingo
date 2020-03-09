from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from jinja2 import Template

from flamingo.plugins.rst.base import parse_rst


TEMPLATE = Template("""
<div class="wy-table-responsive">
    <table class="docutils">
        <thead>
            <tr>
                {% for col in rows[0] %}
                    <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in rows[1:] %}
                <tr>
                    {% for col in row %}
                        <td>{{ col }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
<div>
""")


def table(context):
    class Table(Directive):
        optional_arguments = 0
        has_content = True

        def run(self):
            rows = '\n'.join(self.content).split('\n\n\n')

            for index, item in enumerate(rows):
                rows[index] = [parse_rst(i, context)
                               for i in item.split('\n\n')]

            return [
                raw('', TEMPLATE.render(rows=rows), format='html'),
            ]

    return Table


class rstTable:
    def parser_setup(self, context):
        directives.register_directive('table', table(context))
