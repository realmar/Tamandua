"""This module contains all resource classes used by the REST interface."""

from flask import request
from flask_restful import Resource

from typing import List

from .data_finder import DataFinder
from ..expression.builder import Expression
from ..repository.factory import RepositoryFactory


class BaseResource(Resource):
    def __init__(self, dataFinder: DataFinder):
        self._dataFinder = dataFinder


class Columns(BaseResource):
    """Resource which provides column names."""

    def get(self) -> list:
        return self._dataFinder.availableFields


class Tags(BaseResource):
    """"""

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
            'total_rows': len(results),
            'rows': list(results),
        }


class Count(BaseResource):
    """"""

    def post(self) -> int:
        expression = Expression(request.get_json())
        results = self._dataFinder.search(expression)

        return len(results)


class AdvancedCount(BaseResource):
    """"""

    def post(self, length: int) -> dict:
        expression = Expression(request.get_json())
        results = self._dataFinder.mapreduce(expression)

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
    """"""

    def __init__(self, dataFinder: DataFinder):
        super().__init__(dataFinder)
        self._repository = RepositoryFactory.create_repository()

    def get(self, field: str, maxChoices: int) -> List[str]:
        separator = None
        if field == 'virusresult':
            separator = '('

        return self._repository.get_choices_for_field(field,
                                                               maxChoices,
                                                               separator=separator)