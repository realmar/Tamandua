"""Module which contains the Expression and associated classes, like the ExpressionBuilder."""


from argparse import Namespace
from datetime import datetime

from ..constants import TIME_FORMAT
from .exceptions import ExpressionInvalid


class StringIsNotAComperator(Exception):
    """Thrown when a Comparator cannot be constructed because the given string is not a known comparator."""

    def __init__(self):
        super().__init__("The given string is not a comparator")


class Comparator():
    """Represent a comparator."""

    greater = '>'
    less = '<'
    greater_or_equal = '>='
    less_or_equal = '<='
    equal = '='
    not_equal = '!='
    regex = 're'            # case sensitive
    regex_i = 're_i'        # case insensitive

    def __init__(self, comperator: str):
        """Constructor of Comparator."""

        for c in [y for x, y in vars(Comparator).items() if x[:2] != '__']:
            if comperator == c:
                self.comparator = c
                return

        raise StringIsNotAComperator()

    def is_regex(self) -> bool:
        """Check if the current comparator is a regex comparator."""
        
        if self.comparator == self.regex or \
            self.comparator == self.regex_i:
            return True
        else:
            return False

    def is_regex_case_insensitive(self) -> bool:
        """Check if the current comparator is a case insensitive regex comparator."""

        if self.comparator == self.regex_i:
            return True
        else:
            return False


class Expression():
    """This is Tamandua'a intermediate query language, also known as intermediate expression."""

    def __init__(self, expression: dict=None):
        """Constructor of Expression."""

        self.fields = []
        self.datetime = Namespace(start=None, end=None)
        self.advcount = Namespace(field=None, sep=None)

        if isinstance(expression, dict):
            self.__parse(expression)

    def __parse(self, expression: dict) -> None:
        """Validate and parse an expression which is in a portable format to an intermediate expression."""

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

    def make_portable(self) -> dict:
        """Transform the current expression in a portable format."""

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

        return exp


class ExpressionField():
    """
    Represents a field in an expression.

    A field consists out of a key, value and a Comparator which
    combines the given value with the value stored using the given key.

    Eg.: value > obj[key]
    """

    def __init__(self, key: str, value: str, comparator: Comparator):
        """Constructor of ExpressionField."""

        self.comparator = comparator
        self.value = value
        self.key = key

    def make_portable(self) -> dict:
        """Bring the an expression field in a portable form."""

        return {
            self.key: {
                'comparator': self.comparator,
                'value': self.value
            }
        }


class ExpressionBuilder():
    """Builder which helps making expressions."""

    def __init__(self):
        """Constructor of ExpressionBuilder."""
        self.expression = Expression()

    def add_field(self, field: ExpressionField) -> 'ExpressionBuilder':
        """Add a field to the expression."""
        self.expression.fields.append(field)
        return self

    def set_start_datetime(self, dt: datetime) -> 'ExpressionBuilder':
        """Set the start datetime."""
        self.expression.datetime.start = dt
        return self

    def set_end_datetime(self, dt: datetime) -> 'ExpressionBuilder':
        """Set the end datetime."""
        self.expression.datetime.end = dt
        return self
