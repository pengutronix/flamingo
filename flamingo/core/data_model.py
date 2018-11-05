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


class Lookup:
    def __init__(self, **raw_lookup):
        if len(raw_lookup.keys()) > 1:
            raise ValueError

        raw_field = list(raw_lookup.keys())[0]
        self.value = raw_lookup[raw_field]

        # parse field
        raw_field = raw_field.split('__')

        self.field_name = raw_field.pop(0)

        # parse 'not'
        if raw_field and raw_field[0] == 'not':
            raw_field.pop(0)
            self.negated = True

        else:
            self.negated = False

        # parse logic function
        self.logic_function_name = 'eq'

        if raw_field:
            if raw_field[0] not in LOGIC_FUNCTIONS:
                raise ValueError(
                    'logic function "{}" unknown'.format(raw_field[0]))

            self.logic_function_name = raw_field[0]

        self.logic_function = LOGIC_FUNCTIONS[self.logic_function_name]

    def __repr__(self):
        lookup_name = self.field_name

        if self.negated:
            lookup_name += '__not'

        if self.logic_function_name != 'eq':
            lookup_name += '__{}'.format(self.logic_function_name)

        return '<Lookup({}={})>'.format(lookup_name, repr(self.value))

    def check(self, obj):
        try:
            result = self.logic_function(obj[self.field_name], self.value)

        except TypeError:
            result = False

        if self.negated:
            result = not result

        return result


class LookupSet:
    def __init__(self, **raw_lookups):
        self.lookup_set = []

        for k, v in raw_lookups.items():
            self.lookup_set.append(Lookup(**{k: v}))

    def check(self, obj):
        for lookup in self.lookup_set:
            if not lookup.check(obj):
                return False

        return True

    def __repr__(self):
        return '<LookupSet({})>'.format(repr(self.lookup_list)[1:-1])


class Content:
    def __init__(self, **data):
        self.data = data

    def __repr__(self):
        return '<Content({})>'.format(
            ', '.join(
                ['{}={}'.format(k, repr(v)) for k, v in self.data.items()
                 if k != 'content']
            )
        )

    def __str__(self):
        content = self['content']

        if not content:
            return ''

        return str(content)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        return None

    def __setitem__(self, key, item):
        return self.data.__setitem__(key, item)


class ContentSet:
    def __init__(self, contents=None):
        self.contents = contents or []

    def add(self, *contents, **data):
        if contents:
            self.contents.extend(contents)

        if data:
            self.add(Content(**data))

    def filter(self, **raw_lookups):
        content_set = self.__class__()
        lookup_set = LookupSet(**raw_lookups)

        for content in self.contents:
            if lookup_set.check(content):
                content_set.add(content)

        return content_set

    def exclude(self, **raw_lookups):
        content_set = self.__class__()
        lookup_set = LookupSet(**raw_lookups)

        for content in self.contents:
            if not lookup_set.check(content):
                content_set.add(content)

        return content_set

    def get(self, **raw_lookups):
        if raw_lookups:
            contents = self.filter(**raw_lookups)

        else:
            contents = self.contents

        if len(contents) > 1:
            raise ValueError('Ambiguous query')

        if len(contents) < 1:
            return None

        return contents[0]

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

    def __repr__(self):
        return '<ContentSet({})>'.format(repr(self.contents)[1:-1])
