"""This module contains all resource classes used by the REST interface."""

from flask import request
from flask_restful import Resource
from .data_finder import DataFinder


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
        expression = request.get_json()
        page_start = page * size

        results = self._dataFinder.search(expression)

        return {
            'total_rows': len(results),
            'rows': results[page_start:page_start + size],
        }
