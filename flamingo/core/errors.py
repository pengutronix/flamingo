class FlamingoError(Exception):
    pass


class DataModelError(FlamingoError):
    pass


class MultipleObjectsReturned(DataModelError):
    def __init__(self, query, *args, **kwargs):
        self.query = query

        return super().__init__(*args, **kwargs)

    def __str__(self):
        return 'multiple objects returned for query {}'.format(self.query)


class ObjectDoesNotExist(DataModelError):
    def __init__(self, query, *args, **kwargs):
        self.query = query

        return super().__init__(*args, **kwargs)

    def __str__(self):
        return 'no object returned for query {}'.format(self.query)
