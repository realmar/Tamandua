"""Module used by the webapp: backend to search the data."""

from typing import Dict, Tuple
from datetime import datetime

from .. import constants
from ..expression.exceptions import ExpressionInvalid
from ..repository.factory import RepositoryFactory
from ..repository.misc import SearchScope, CountableIterator
from ..expression.builder import Expression


class DataFinder():
    """
    DataFinder encapsulates the repository.

    This is kind of a legacy component and should be refactored
    directly into the different resourcees in rest_api.
    That because DataFinder contains only very little logic
    which is not enough to justify the existence of this class.
    """

    def __init__(self):
        self._repository = RepositoryFactory.create_repository()

        self.availableFields = self._repository.get_all_keys()
        self.availableTags = self._repository.get_all_tags()

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

    def mapreduce(self, expression: Expression) -> CountableIterator:
        """"""

        """
        This specific expression has to have additional attributes:
        
        {
            ...
            
            "countfield": "<field>",
            "sep": "<separator>"
            
            ...
        }
        
        """

        if expression.advcount.field is None:
            raise ExpressionInvalid('advcount.field is required. Provide it in your expression.')

        return self._repository.count_specific_fields(expression)

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

