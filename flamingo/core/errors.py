class FlamingoError(Exception):
    pass


class DataModelError(FlamingoError):
    pass


class MultipleObjectsReturned(DataModelError):
    def __init__(self, query, *args, **kwargs):
        self.query = query

        return super().__init__(*args, **kwargs)

    def __str__(self):
        return f"multiple objects returned for query {self.query}"


class ObjectDoesNotExist(DataModelError):
    def __init__(self, query, *args, **kwargs):
        self.query = query

        return super().__init__(*args, **kwargs)

    def __str__(self):
        return f"no object returned for query {self.query}"
