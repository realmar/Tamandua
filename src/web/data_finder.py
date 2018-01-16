"""Module used by the webapp: backend to search the data."""

from typing import Dict, List, Callable
from datetime import datetime

from functools import partial

from .. import constants
from ..repository.factory import RepositoryFactory
from ..repository.misc import SearchScope, CountableIterator
from ..expression.builder import Expression
from .cache import DataCache


FieldChoicesResults = List[str]

GLOB_CACHE_INTERVAL = 60 * 60 * 12


class FieldChoicesData():
    """Encapsulate getting, storing and caching choices for a given field."""

    CACHE_INTERVAL = GLOB_CACHE_INTERVAL

    def __init__(self, field: str, maxChoices: int):
        """Constructor of FieldChoicesData."""
        self._repository = RepositoryFactory.create_repository()

        self._field = field
        self._maxChoices = maxChoices

        self._data = DataCache(self.__make_data_func(), self.CACHE_INTERVAL)

    @staticmethod
    def __transform_datetime_to_string(fields: FieldChoicesResults) -> FieldChoicesResults:
        transformed = []

        for field in fields:
            if isinstance(field, datetime):
                transformed.append(datetime.strftime(field, constants.TIME_FORMAT))
            else:
                transformed.append(field)

        return transformed

    def __make_data_func(self) -> Callable[[], FieldChoicesResults]:
        """Construct the caching function."""
        separator = None
        if self._field == 'virusresult':
            separator = '('

        dataFunc = partial(self._repository.get_choices_for_field,
                       field=self._field,
                       limit=self._maxChoices,
                       separator=separator)

        return lambda *args: FieldChoicesData.__transform_datetime_to_string(dataFunc(*args))

    def get_data(self, maxChoices: int):
        """Return choices for a given field."""
        if maxChoices != self._maxChoices:
            self._maxChoices = maxChoices
            self._data = DataCache(
                self.__make_data_func(),
                self.CACHE_INTERVAL)

        return self._data.data



class DataFinder():
    """
    DataFinder encapsulates the repository.

    It also caches data, like available fields, tags or the fieldchoices.
    """

    CACHE_INTERVAL = GLOB_CACHE_INTERVAL

    def __init__(self):
        self._repository = RepositoryFactory.create_repository()

        self._availableFields = DataCache(self._repository.get_all_keys, self.CACHE_INTERVAL)
        self._availableTags = DataCache(self._repository.get_all_tags, self.CACHE_INTERVAL)
        self._choices_for_fields = {}

    @property
    def availableFields(self):
        return self._availableFields.data

    @property
    def availableTags(self):
        return self._availableTags.data

    def search(self, expression: Expression) -> CountableIterator[Dict]:
        """Search for specific mails."""

        """
        Description of an expression:
        
        {
            "fields": [
                { "field1": {
                        "comparator": "=|<|>",
                        "value": "value1"
                    }
                },
                { "field2": {
                        "comparator": "=|<|>",
                        "value": "value2"
                    }
                }
                ...
            ],
            
            "datetime": {
                "start": "time-str",
                "end": "time-str"
            }
        }
        
        The fields described in "fields" have to match to the fields of the mail
        additionally should the mail be processed between datetime.start and datetime.end
        (including datetime.end)
        
        This is not a generic solution, although still one that provides the user with great flexibility.
        """

        """
        Validation of fields
        """

        return self._repository.find(expression, SearchScope.ALL)

    def get_choices_for_field(self, field: str, maxChoices: int) -> FieldChoicesResults:
        """Get available choices for a given field and cache them."""
        try:
            return self._choices_for_fields[field].get_data(maxChoices)
        except KeyError as e:
            fd = FieldChoicesData(field, maxChoices)
            self._choices_for_fields[field] = fd

            return fd.get_data(maxChoices)

    def count_specific_fields(self, expression: Expression, field: str, separator: str = None) -> CountableIterator:
        """"""

        return self._repository.count_specific_fields(expression, field, separator)

    def filter_page_size(self, results: CountableIterator[Dict], page_start: int, page_size: int) -> CountableIterator[Dict]:
        """Filter a search result to match the pager."""

        results_list = []

        for i in range(0, page_start + page_size):
            try:
                currResult = next(results)
            except StopIteration as e:
                break

            if i < page_start:
                continue

            self._repository.remove_metadata(currResult)

            timeMap = {
                constants.PHD_MXIN_TIME: currResult.get(constants.PHD_MXIN_TIME),
                constants.PHD_IMAP_TIME: currResult.get(constants.PHD_IMAP_TIME)
            }

            for key, value in timeMap.items():
                if value is not None:
                    if isinstance(value, list):
                        tmp = []
                        for v in value:
                            tmp.append(datetime.strftime(v, constants.TIME_FORMAT))

                        currResult[key] = tmp
                    else:
                        currResult[key] = datetime.strftime(value, constants.TIME_FORMAT)

            results_list.append(currResult)

        return CountableIterator(iter(results_list), lambda x: len(results))

