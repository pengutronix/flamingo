from datetime import date, datetime
import re


class HTML5TimeTag:
    TIME_FORMAT = re.compile(r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})( (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2})(:(?P<second>[0-9]{2}))?)?')  # NOQA

    def __init__(self, time_object, context):
        self.time_object = time_object

        if isinstance(self.time_object, str):
            try:
                time = self.TIME_FORMAT.search(self.time_object).groupdict()

            except AttributeError:
                raise ValueError('string doesnt match the time format')

            keys = time.keys()

            if len(keys) == 6:  # datetime
                self.time_object = date(time['year'], time['month'],
                                        time['day'])

            else:  # date
                self.time_object = datetime(time['year'], time['month'],
                                            time['day'], time['hour'],
                                            time['minute'], time['second'])

        self.context = context

    def _comp(self, other, comp):
        if isinstance(other, self.__class__):
            return comp(self.time_object, other.time_object)

        else:
            return comp(self.time_object, other)

    def __eq__(self, other):
        return self._comp(other, lambda a, b: a == b)

    def __lt__(self, other):
        return self._comp(other, lambda a, b: a < b)

    def __gt__(self, other):
        return self._comp(other, lambda a, b: a > b)

    def __str__(self):
        if isinstance(self.time_object, date):
            strftime_string = getattr(self.context.settings,
                                      'TIME_DATE_FORMAT',
                                      '%a %d. %B %Y')

        elif isinstance(self.time_object, datetime):
            strftime_string = getattr(self.context.settings,
                                      'TIME_DATETIME_FORMAT',
                                      '%a %d. %B %Y, H:%M:%S')

        return '<time datetime="{}">{}</time>'.format(
            str(self.time_object) if isinstance(self.time_object, date)
            else str(self.time_object).rsplit('.', 1)[0],
            self.time_object.strftime(strftime_string),
        )

    def __repr__(self):
        return self.__str__()


class Time:
    def contents_parsed(self, context):
        TIME_FIELD_NAME = getattr(context.settings, 'TIME_FIELD_NAME', 'time')

        for content in context.contents:
            if not content[TIME_FIELD_NAME]:
                continue

            content[TIME_FIELD_NAME] = HTML5TimeTag(content[TIME_FIELD_NAME],
                                                    context)
