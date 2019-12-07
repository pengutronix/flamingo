import operator

from flamingo.core.errors import MultipleObjectsReturned, ObjectDoesNotExist

AND = operator.and_
NOT = operator.not_
OR = operator.or_

QUOTE_KEYS = ('content_body', 'template_context', )


def quote(value):
    types = {
        str: '<str(...)>',
        list: '<[...]>',
        dict: '<{...}>',
        tuple: '<(...)>',
        Content: '<Content(...)>',
        ContentSet: '<ContentSet(...)>',
    }

    t = type(value)

    if t in types:
        return types[t]

    return value


def _str(s):
    return str(s) if s is not None else ''


LOGIC_FUNCTIONS = {
    'eq': lambda a, b: a == b,
    'ne': lambda a, b: a != b,
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'in': lambda a, b: a in b,
    'contains': lambda a, b: _str(b) in _str(a),
    'icontains': lambda a, b: _str(b).lower() in _str(a).lower(),
    'isnull': lambda a, b: a is None if b else a is not None,
    'isfalse': lambda a, b: not bool(a) if b else bool(a),
    'startswith': lambda a, b: _str(a).startswith(b),
    'endswith': lambda a, b: _str(a).startswith(b),
    'passes': lambda a, b: b(a),
}


def Content_default_on_change_handler(content, key, item):
    pass


class F:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "F('{}')".format(self.name)


class Q:
    def __init__(self, *qs, **lookups):
        self.connector = 'AND'
        self.negated = False
        self.qs = None
        self.lookups = None

        if not qs and not lookups:
            raise TypeError('to few arguments')

        if qs and lookups:
            raise TypeError('to many arguments')

        if not lookups and len(qs) == 1 and isinstance(qs[0], dict):
            lookups = qs[0]
            qs = []

        if qs:
            self.qs = qs

        if lookups:
            self.lookups = lookups

    def __repr__(self):
        if self.qs:
            repr_str = ', '.join([
                repr(q) for q in self.qs
            ])

        elif self.lookups:
            repr_str = ', '.join([
                '{}={}'.format(k, repr(v)) for k, v in self.lookups.items()
            ])

        return '<{}{}({})>'.format(
            'NOT ' if self.negated else '',
            self.connector,
            repr_str,
        )

    def __or__(self, other):
        q = Q(self, other)
        q.connector = 'OR'

        return q

    def __and__(self, other):
        return Q(self, other)

    def __invert__(self):
        self.negated = not self.negated

        return self

    def check(self, obj):
        results = []
        end_result = None

        if self.qs:
            for q in self.qs:
                results.append(q.check(obj))

        elif self.lookups:
            for field_name, value in self.lookups.items():
                logic_function = 'eq'

                if '__' in field_name:
                    field_name, logic_function = field_name.split('__')

                if isinstance(value, F):
                    value = obj[value.name]

                try:
                    results.append(
                        LOGIC_FUNCTIONS[logic_function](
                            obj[field_name], value))

                except TypeError:
                    results.append(False)

        if self.connector == 'AND':
            end_result = all(results)

        elif self.connector == 'OR':
            end_result = any(results)

        else:
            raise ValueError("unknown connector '{}'".format(self.connector))

        if self.negated:
            end_result = not end_result

        return end_result


class Content:
    def __init__(self, **data):
        self.data = data
        self.on_change = Content_default_on_change_handler

    def __repr__(self, pretty=True, recursion_stack=None):
        if pretty:
            from flamingo.core.utils.pprint import pformat

            return pformat(self)

        recursion_stack = recursion_stack or []
        repr_string = []

        recursion_stack.append(self)

        for k, v in self.data.items():
            if k in QUOTE_KEYS:
                repr_string.append('{}={}'.format(k, quote(v)))

            elif isinstance(v, (Content, ContentSet)):
                if v in recursion_stack:
                    repr_string.append('{}={}'.format(k, quote(v)))

                else:
                    repr_string.append(
                        '{}={}'.format(
                            k, v.__repr__(pretty=pretty,
                                          recursion_stack=recursion_stack)))

            else:
                repr_string.append('{}={}'.format(k, repr(v)))

        return '<Content({})>'.format(', '.join(repr_string))

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        return None

    def __setitem__(self, key, item):
        return_value = self.data.__setitem__(key, item)
        self.on_change(self, key, item)

        return return_value

    def __contains__(self, key):
        return key in self.data

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)


class ContentSet:
    def __init__(self, contents=None, query=None):
        self.contents = contents or []
        self._query = query

    @property
    def query(self):
        return self._query

    def add(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, Content):
                self.contents.append(arg)

            elif isinstance(arg, dict):
                self.contents.append(Content(**arg))

        if kwargs:
            self.contents.append(Content(**kwargs))

    def _filter(self, negated, *args, **kwargs):
        if not kwargs and len(args) == 1 and isinstance(args[0], dict):
            query = Q(**args[0])

        else:
            query = Q(*args, **kwargs)

        if negated:
            query = ~query

        content_set = self.__class__(
            query=self.query & query if self.query else query)

        for content in self.contents:
            if query.check(content):
                content_set.add(content)

        return content_set

    def filter(self, *args, **kwargs):
        return self._filter(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        return self._filter(True, *args, **kwargs)

    def get(self, *args, **kwargs):
        if args or kwargs:
            contents = self.filter(*args, **kwargs)

        else:
            contents = self

        if len(contents) > 1:
            raise MultipleObjectsReturned(query=contents.query)

        if len(contents) < 1:
            raise ObjectDoesNotExist(query=contents.query)

        return contents[0]

    def exists(self):
        if len(self.contents) > 0:
            return True

        return False

    def first(self):
        if len(self.contents) < 1:
            raise ObjectDoesNotExist(query=self.query)

        return self.contents[0]

    def last(self):
        if len(self.contents) < 1:
            raise ObjectDoesNotExist(query=self.query)

        return self.contents[-1]

    def values(self, *field_names):
        return_values = []

        for content in self:
            return_values.append(tuple())

            for field_name in field_names:
                return_values[-1] += (content[field_name], )

            if len(field_names) == 1:
                if return_values[-1][0] is None:
                    return_values.pop()

                else:
                    return_values[-1] = return_values[-1][0]

        if len(field_names) == 1:
            dirty_return_values = return_values
            return_values = []

            for i in dirty_return_values:
                if i not in return_values:
                    return_values.append(i)

        return return_values

    def order_by(self, field_name):
        reverse = False

        if field_name.startswith('-'):
            field_name = field_name[1:]
            reverse = True

        return self.__class__(
            contents=sorted(
                self.contents,
                key=lambda x: (x[field_name] is None, x[field_name]),
                reverse=reverse,
            )
        )

    def count(self):
        return len(self.contents)

    def __len__(self):
        return self.contents.__len__()

    def __getitem__(self, key):
        contents = self.contents.__getitem__(key)

        if isinstance(key, slice):
            contents = self.__class__(contents=contents)

        return contents

    def __iter__(self):
        return self.contents.__iter__()

    def __repr__(self, pretty=True, recursion_stack=None):
        if pretty:
            from flamingo.core.utils.pprint import pformat

            return pformat(self)

        repr_strings = []
        recursion_stack = recursion_stack or []

        recursion_stack.append(self)

        for content in self.contents:
            repr_strings.append(
                content.__repr__(pretty=pretty,
                                 recursion_stack=recursion_stack))

        return '<ContentSet({})>'.format(', '.join(repr_strings))

    def __add__(self, other):
        if not isinstance(other, (ContentSet, Content)):
            raise TypeError("unsupported operand type(s) for '+'")

        if isinstance(other, Content):
            return ContentSet(contents=self.contents+[other])

        else:
            return ContentSet(contents=self.contents+other.contents)

    def __iadd__(self, other):
        if not isinstance(other, (ContentSet, Content)):
            raise TypeError("unsupported operand type(s) for '+='")

        if isinstance(other, Content):
            self.add(other)

        else:
            self.add(other.contents)

        return self

    def __sub__(self, other):
        if not isinstance(other, (ContentSet, Content)):
            raise TypeError("unsupported operand type(s) for '-'")

        content_set = ContentSet(contents=self.contents)

        if isinstance(other, Content):
            content_set.contents.remove(other)

        else:
            for content in other.contents:
                content_set.contents.remove(content)

        return content_set

    def __isub__(self, other):
        if not isinstance(other, (ContentSet, Content)):
            raise TypeError("unsupported operand type(s) for '-='")

        if isinstance(other, Content):
            self.contents.remove(other)

        else:
            for content in other.contents:
                self.contents.remove(content)

        return self
