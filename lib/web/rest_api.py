"""This module contains all resource classes used by the REST interface."""


from flask import request
from flask_restful import Resource
from .data_finder import DataFinder
from .. import constants


class BaseResource(Resource):
    def __init__(self, dataFinder: DataFinder):
        self._dataFinder = dataFinder


class Columns(BaseResource):
    """Resource which provides column names."""

    _essentialFields = [
        constants.PHD_MXIN_TIME,
        'sender',
        'recipient'
    ]

    _breakcolumn = 'xs sm md lg'
    _nobreak = ''

    def get(self) -> list:
        rawColumns = self._dataFinder.availableFields
        columns = []

        for c in rawColumns:
            breakpoints = self._breakcolumn
            if c in self._essentialFields:
                breakpoints = self._nobreak

            columns.append({
                'name': c,
                'title': c,
                'breakpoints': breakpoints
            })

        return columns


class Search(BaseResource):
    """Resource which provides searching mechanisms."""

    """
    # for debugging
    expression = {
        "fields" : [
            { "sender": "lionel" }
        ],

        "datetime": {
            "start": "2017/01/19 22:51:45",
            "end": "2017/01/19 22:55:50"
        }
    }
    
    # one line    
    {"fields" : [{ "sender": "lionel" }],"datetime": {"start": "2017/01/19 22:51:45","end": "2017/01/19 22:55:50"}}
    """

    _default_page_size = 20

    def post(self, page: int) -> list:
        expression = request.get_json()
        page_size = expression.get('page_size')
        if not isinstance(page_size, int):
            page_size = self._default_page_size
        page_start = page * page_size

        results = self._dataFinder.search(expression)

        return results[page_start:page_start + page_size]