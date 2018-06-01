"""This module contains all resource classes used by the REST interface."""

from typing import List, Any

from datetime import datetime, timedelta
from flask import request
from flask_restful import Resource

from .exceptions import InvalidFieldValues, MissingFields
from .data_finder import DataFinder, FieldChoicesResults
from ..expression.builder import Expression
from ..constants import TIME_FORMAT


class BaseResource(Resource):
    """Base class of all resources."""

    def __init__(self, dataFinder: DataFinder):
        self._dataFinder = dataFinder


class Columns(BaseResource):
    """Resource which provides column names."""

    def get(self) -> list:
        return self._dataFinder.availableFields


class Tags(BaseResource):
    """Resource represents available tags."""

    def get(self) -> list:
        return self._dataFinder.availableTags


class Search(BaseResource):
    """Resource which provides searching mechanisms."""

    """
    # for debugging
    expression = {
        "fields" : [
            { "sender": {
                "comparator: "=",
                "value": "lionel" 
            }
        ],

        "datetime": {
            "start": "2017/01/19 22:51:45",
            "end": "2017/01/19 22:55:50"
        }
    }
    
    # one line    
    {"fields" : [{ "sender": "lionel" }],"datetime": {"start": "2017/01/19 22:51:45","end": "2017/01/19 22:55:50"}}
    """

    def post(self, page: int, size: int) -> dict:
        expression = Expression(request.get_json())
        page_start = page * size

        results = self._dataFinder.filter_page_size(
            self._dataFinder.search(expression),
            page_start,
            size
        )

        return {
            # we do not want to count the results as this will
            # double the request time
            'total_rows': 0, # len(results),
            'rows': list(results),
        }


class Count(BaseResource):
    """Count the returned objected of a given search query."""

    def post(self) -> int:
        expression = Expression(request.get_json())
        results = self._dataFinder.search(expression)

        return len(results)


class AdvancedCount(BaseResource):
    """
    Count occurrences of values in a given field.

    This resource is used by the View::Dashboard for the
    top n lists.
    """

    def post(self, field: str, length: int, separator: str = None) -> dict:
        expression = Expression(request.get_json())
        results = self._dataFinder.count_specific_fields(expression, field, separator)

        final = []
        for i in range(0, length):
            try:
                final.append(next(results))
            except StopIteration as e:
                break

        return {
            'items': final,
            'total': len(results)
        }


class FieldChoices(BaseResource):
    """Distinct choices of a given field."""

    def __init__(self, dataFinder: DataFinder):
        super().__init__(dataFinder)

    def get(self, field: str, maxChoices: int) -> FieldChoicesResults:
        return self._dataFinder.get_choices_for_field(field, maxChoices)


class SupportedFieldChoices(BaseResource):
    """List of supported field choices."""

    def __init__(self, dataFinder: DataFinder):
        super().__init__(dataFinder)

    def get(self) -> List[str]:
        """Return a list of the field names where the fieldchoices endpoint is applicable."""
        return DataFinder.SUPPORTED_FIELD_CHOICES


class Trend(BaseResource):
    """Trend over time of a given expression"""

    def __init__(self, dataFinder: DataFinder):
        super().__init__(dataFinder)

    def post(self, field: str, dataCount: int, separator: str = None):
        json = request.get_json()
        totalHours = json.get('totalHours')
        sampleCount = json.get('sampleCount')
        expression = Expression(json)

        self.__ensure_fields(totalHours, sampleCount)
        self.__ensure_type(int, totalHours, sampleCount)

        interval = totalHours / sampleCount
        dt = datetime.now() - timedelta(hours=totalHours) + timedelta(hours=interval)

        data = []

        for i in range(0, sampleCount):
            expression.datetime.start = dt - timedelta(hours=interval)
            expression.datetime.end = dt

            results = self._dataFinder.count_specific_fields(expression, field, separator)
            evalResults = []
            for i in range(0, dataCount):
                try:
                    evalResults.append(next(results))
                except StopIteration:
                    break

            if len(evalResults) > 0:
                for r in evalResults:
                    r['datetime'] = expression.datetime.start.strftime(TIME_FORMAT)
                data.append(evalResults)

            dt = dt + timedelta(hours=interval)

        return data

    @staticmethod
    def __ensure_fields(*fields: Any) -> None:
        for field in fields:
            if field is None:
                raise MissingFields('WIP')

    @staticmethod
    def __ensure_type(type: Any, *fields: Any) -> None:
        for field in fields:
            if not isinstance(field, type):
                raise InvalidFieldValues('WIP')
