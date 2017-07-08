""""""


from argparse import Namespace
from datetime import datetime

from ..constants import TIME_FORMAT
from .exceptions import ExpressionInvalid


class StringIsNotAComperator(Exception):
    def __init__(self):
        super().__init__("The given string is not a comparator")


class Comparator():
    greater = '>'
    less = '<'
    greater_or_equal = '>='
    less_or_equal = '<='
    equal = '='
    not_equal = '!='

    def __init__(self, comperator: str):
        for c in (self.equal, self.less, self.greater, self.not_equal, self.greater_or_equal, self.less_or_equal):
            if comperator == c:
                self.comparator = c
                return

        raise StringIsNotAComperator()


class Expression():
    """"""

    def __init__(self, expression: dict=None):
        self.fields = []
        self.datetime = Namespace(start=None, end=None)
        self.advcount = Namespace(field=None, regex=None)

        if isinstance(expression, dict):
            self.__parse(expression)

    def __parse(self, expression: dict) -> None:
        try:
            fields = expression['fields']
        except KeyError as e:
            fields = []

        """
        Validation of fields
        """

        counter = 0
        for f in fields:
            currField = 'fields.' + str(counter) + ' '

            if not isinstance(f, dict):
                raise ExpressionInvalid(currField + 'is not a dict')
            else:
                if len(f) > 1:
                    raise ExpressionInvalid(currField + 'has more than 1 key value pair')

            k, v = next(iter(f.items()))

            if v.get('value') is None:
                raise ExpressionInvalid(currField + 'has no value key')

            try:
                if not isinstance(v['comparator'], str):
                    raise ExpressionInvalid(currField + 'comparator key is not a string')
            except KeyError as e:
                raise ExpressionInvalid(currField + 'has no comparator key')

            counter += 1

            self.fields.append(ExpressionField(k, v['value'], v['comparator']))

        """
        Validation of datetime strings
        """

        datetimeRaw = expression.get('datetime')
        startTimeRaw = None
        endTimeRaw = None

        if datetimeRaw is not None:
            startTimeRaw = datetimeRaw.get('start')
            endTimeRaw = datetimeRaw.get('end')

            if not isinstance(startTimeRaw, str) or startTimeRaw.strip() == "":
                startTimeRaw = None

            if not isinstance(endTimeRaw, str) or endTimeRaw.strip() == "":
                endTimeRaw = None

        if startTimeRaw is not None:
            try:
                self.datetime.start = datetime.strptime(startTimeRaw, TIME_FORMAT)
            except Exception as e:
                raise ExpressionInvalid("From datetime format is invalid: " + str(startTimeRaw))

        if endTimeRaw is not None:
            try:
                self.datetime.end = datetime.strptime(endTimeRaw, TIME_FORMAT)
            except Exception as e:
                raise ExpressionInvalid("To datetime format is invalid: " + str(endTimeRaw))

        """
        Validation advcount
        """

        try:
            self.advcount.field = expression['advcount']['field']
        except KeyError as e:
            pass
        else:
            try:
                self.advcount.regex = expression['advcount']['regex']
            except KeyError as e:
                pass

    def make_portable(self) -> dict:
        exp = {}
        if len(self.fields) > 0:
            exp['fields'] = []

            for f in self.fields:
                exp['fields'].append(f.make_portable())

        if self.datetime.start is not None or self.datetime.end is not None:
            exp['datetime'] = {}

            if self.datetime.start is not None:
                exp['datetime']['start'] = self.datetime.start.stftime(TIME_FORMAT)

            if self.datetime.end is not None:
                exp['datetime']['end'] = self.datetime.end.stftime(TIME_FORMAT)

        if self.advcount.field is not None:
            exp['advcount'] = {'field': self.advcount.field}

            if self.advcount.regex is not None:
                exp['advcount']['regex'] = self.advcount.regex

        return exp


class ExpressionField():
    """"""

    def __init__(self, key: str, value: str, comparator: Comparator):
        self.comparator = comparator
        self.value = value
        self.key = key

    def make_portable(self) -> dict:
        return {
            self.key: {
                'comparator': self.comparator,
                'value': self.value
            }
        }


class ExpressionBuilder():
    """"""

    def __init__(self):
        self.expression = Expression()

    def add_field(self, field: ExpressionField) -> None:
        self.expression.fields.append(field)
        return self

    def set_count_field(self, field: str) -> None:
        self.expression.advcount.field = field
        return self

    def set_count_regex(self, regex: str) -> None:
        self.expression.advcount.regex = regex
        return self

    def set_start_datetime(self, dt: datetime) -> None:
        self.expression.datetime.start = dt
        return self

    def set_end_datetime(self, dt: datetime) -> None:
        self.expression.datetime.end = dt
        return self