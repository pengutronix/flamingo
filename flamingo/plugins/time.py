import datetime
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

            # datetime
            if len(time.keys()) == 3:
                self.time_object = datetime.date(
                    time['year'],
                    time['month'],
                    time['day'],
                )

            # date
            else:
                self.time_object = datetime.datetime(
                    time['year'],
                    time['month'],
                    time['day'],
                    time['hour'],
                    time['minute'],
                    time['second'],
                )

        self.context = context

    def strftime(self, *args, **kwargs):
        return self.time_object.strftime(*args, **kwargs)

    def _comp(self, other, comp):
        self_time_object = self.time_object

        if not isinstance(self_time_object, datetime.datetime):
            self_time_object = datetime.datetime.combine(
                self_time_object, datetime.datetime.min.time())

        other_time_object = other

        if isinstance(other_time_object, self.__class__):
            other_time_object = other_time_object.time_object

        if not isinstance(other_time_object, datetime.datetime):
            other_time_object = datetime.datetime.combine(
                other_time_object, datetime.datetime.min.time())

        return comp(self_time_object, other_time_object)

    def __eq__(self, other):
        return self._comp(other, lambda a, b: a == b)

    def __lt__(self, other):
        return self._comp(other, lambda a, b: a < b)

    def __gt__(self, other):
        return self._comp(other, lambda a, b: a > b)

    def __le__(self, other):
        return self._comp(other, lambda a, b: a <= b)

    def __ge__(self, other):
        return self._comp(other, lambda a, b: a >= b)

    def __str__(self):
        if isinstance(self.time_object, datetime.datetime):
            strftime_string = getattr(self.context.settings,
                                      'TIME_DATE_FORMAT',
                                      '%a %d. %B %Y')

        elif isinstance(self.time_object, datetime.date):
            strftime_string = getattr(self.context.settings,
                                      'TIME_DATETIME_FORMAT',
                                      '%a %d. %B %Y, H:%M:%S')

        return '<time datetime="{}">{}</time>'.format(
            str(self.time_object)
            if isinstance(self.time_object, datetime.date)
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
