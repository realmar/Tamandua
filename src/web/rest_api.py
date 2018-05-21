"""This module contains all resource classes used by the REST interface."""

from typing import List, Dict, Tuple

from flask import request
from flask_restful import Resource

from datetime import datetime, timedelta

from .exceptions import MissingFields, InvalidFieldValues
from .data_finder import DataFinder, FieldChoicesResults
from ..expression.builder import Expression, ExpressionBuilder, ExpressionField, Comparator


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


class DirectedGraph(BaseResource):
    """Construct a directed graph from a sender mail."""

    def __init__(self, dataFinder: DataFinder):
        super().__init__(dataFinder)

    def post(self, email: str) -> Dict[str, list]:
        data = request.get_json()

        # extract data
        hours = data.get('hours')
        depth = data.get('depth')

        # validate data
        if hours is None:
            raise MissingFields('hours')

        if depth is None:
            raise MissingFields('depth')

        if not isinstance(hours, int):
            raise InvalidFieldValues('hours')

        if not isinstance(depth, int):
            raise InvalidFieldValues('depth')

        # generate graph
        nodes = [email]
        edges = []

        self.__get_next(nodes, edges, email, hours, depth)

        return {
            'nodes': nodes,
            'edges': [{'source': edge[0], 'target': edge[1]} for edge in edges]
        }

    def __get_next(self,
                   nodes: List[str],
                   edges: List[Tuple[str, str]],
                   sender: str,
                   hours: int,
                   max_depth: int,
                   current_depth: int = 0) -> None:

        builder = ExpressionBuilder()\
            .add_field(ExpressionField('sender', sender, Comparator.equal))\
            .set_start_datetime(datetime.now() - timedelta(hours=hours))\
            .set_end_datetime(datetime.now() + timedelta(hours=1))

        results = self._dataFinder.search(builder.expression)

        for result in results:
            recipients = result.get('recipient')
            if not isinstance(recipients, list):
                recipients = [recipients]

            for recipient in recipients:
                if recipient is None:
                    continue

                hasNode = recipient in nodes
                if not hasNode:
                    nodes.append(recipient)

                if not self.__has_edge(sender, recipient, edges):
                    edges.append((sender, recipient))

                if not hasNode and current_depth < max_depth:
                    self.__get_next(nodes, edges, recipient, hours, max_depth, current_depth + 1)

    @staticmethod
    def __has_edge(source: str, target: str, edges: List[Tuple[str, str]]) -> bool:
        """Check if edge exists."""

        for edge in edges:
            if source == edge[0] and target == edge[1]:
                return True

        return False
