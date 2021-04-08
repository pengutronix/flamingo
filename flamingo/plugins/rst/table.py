import logging
import re

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from flamingo.plugins.rst import register_directive

COLUMN_RE = re.compile(r'([\^\|])([^\^\|]+)?')

logger = logging.getLogger('flamingo.plugins.rstTable')


def gen_directive(context, plugin):
    class Table(Directive):
        required_arguments = 0
        has_content = True

        option_spec = {
            'template': directives.unchanged,
        }

        def _run(self):
            self.row = 1
            rows = []

            for string in self.content:
                self.row += 1

                if not string.strip():
                    continue

                row = []
                columns = COLUMN_RE.findall(string)

                if not columns:
                    raise ValueError

                for column_type, column_content in columns:
                    column = {
                        'tag_name': 'td',
                        'content': column_content,
                        'skip': False,
                        'attributes': {
                            'align': 'left',
                            'colspan': 1,
                            'rowspan': 1,
                        },
                    }

                    if column_type == '^':
                        column['tag_name'] = 'th'

                    row.append(column)

                rows.append(row)

            # remove trailing column
            self.row = 1
            remove_trailing_column = True

            for row in rows:
                self.row += 1

                if row[-1]['content'].strip():
                    remove_trailing_column = False

                    break

            if remove_trailing_column:
                self.row = 1

                for row in rows:
                    self.row += 1
                    row.remove(row[-1])

            # add styling attributes
            self.row = 1

            def merge_horizontal(row_index, col_index):
                row = rows[row_index]
                col = row[col_index]

                col['skip'] = True

                while col_index > -1:
                    col_index -= 1
                    col = row[col_index]

                    if col['content'] != '':
                        col['attributes']['colspan'] += 1

                        return

            def merge_vertical(row_index, col_index):
                row = rows[row_index]
                col = row[col_index]

                col['skip'] = True

                while row_index > -1:
                    row_index -= 1
                    row = rows[row_index]
                    col = row[col_index]

                    if col['content'].strip() != ':::':
                        col['attributes']['rowspan'] += 1

                        return

            for row_index, row in enumerate(rows):
                self.row += 1

                for col_index, col in enumerate(row):
                    content = col['content']

                    left_padded = (content.startswith(' ') or
                                   content.startswith('\t'))

                    right_padded = (content.endswith(' ') or
                                    content.endswith('\t'))

                    # text align
                    if left_padded and right_padded:
                        col['attributes']['align'] = 'center'

                    elif left_padded and not right_padded:
                        col['attributes']['align'] = 'right'

                    # merge horizontal
                    if col['content'].strip() == '':
                        merge_horizontal(row_index, col_index)

                    # merge horizontal
                    elif col['content'].strip() == ':::':
                        merge_vertical(row_index, col_index)

            # remove obsolete attributes
            self.row = 1

            for row_index, row in enumerate(list(rows)):
                self.row += 1

                for col_index, col in enumerate(list(row)):
                    if col['attributes']['rowspan'] == 1:
                        col['attributes'].pop('rowspan')

                    if col['attributes']['colspan'] == 1:
                        col['attributes'].pop('colspan')

            # find template
            template_name = self.options.get(
                'template',
                plugin.template_name,
            )

            # render template
            html = context.templating_engine.render(
                template_name=template_name,
                template_context={
                    'context': context,
                    'rows': rows,
                },
                handle_exceptions=False,
            )

            return [raw('', html, format='html')]

        def run(self):
            try:
                return self._run()

            except Exception:
                path = context.content['path']
                offset = plugin.rst_base_plugin.offsets.get(path, 0)
                lineno = offset + self.lineno + self.row

                logger.error(
                    "%s:%s invalid table format",
                    path,
                    lineno,
                    exc_info=False,
                )

                return []

    return Table


class rstTable:
    def parser_setup(self, context):
        self.rst_base_plugin = context.plugins.get_plugin('reStructuredText')

        self.rst_directive_names = context.settings.get(
            'RST_TABLE_DIRECTIVE_NAMES',
            ['table'],
        )

        self.template_name = context.settings.get(
            'RST_TABLE_DEFAULT_TEMPLATE',
            'table.html',
        )

        Table = gen_directive(context, self)

        for name in self.rst_directive_names:
            register_directive(name, Table)
