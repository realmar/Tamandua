"""Module which contains the repository implementation for mongodb."""


import itertools
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from pymongo.collection import Collection as PyMongoCollection
import pymongo.errors as pymongo_errors
import re
from functools import partial

from bson.code import Code
from datetime import datetime

from ast import literal_eval

from typing import List, Dict
from .interfaces import IRepository
from .misc import SearchScope, CountableIterator
from ..expression.builder import Comparator, Expression
from .js import Loader
from ..config import Config
from ..constants import get_all_times


class TargetCollectionNotFound(Exception):
    """Thrown when the requested collection was not found."""

    pass


class MongoCountSpecificIterable(CountableIterator):
    """
    Iterable specific to the result set of the
    count_specific_fields method. It behaves the same
    way as a CountableIterator.
    """

    def __init__(self, cursor):
        self.__cursor = cursor
        self.__sum = 0

    def __next__(self):
        x = next(self.__cursor)
        if x['details']['field'] is None or x['details']['field'] == '':
            x['details']['field'] = 'nothing_found'

        if self.__sum == 0:
            self.__sum = x['sum']

        return {'key': x['details']['field'], 'value': x['details']['value']}

    def __len__(self):
        return self.__sum


class MongoRepository(IRepository):
    """Concrete IRepository which uses MongoDB as storage backend."""

    # definition of the document names
    # in the metadata collection
    __lastBytePosName = 'lastbytepos'
    __lastLogfileSizeName = 'lastlogfilesize'
    __lastRunDateTimeName = 'lastrundatetime'


    # map different comparators to the mongodb
    # specific comparators
    __comparatorMap = {
        Comparator.equal: '$eq',
        Comparator.not_equal: '$not',
        Comparator.greater: '$gt',
        Comparator.less: '$lt',
        Comparator.greater_or_equal: '$gte',
        Comparator.less_or_equal: '$lte',
        Comparator.regex: '$regex'
    }

    def __init__(self):
        """Constructor of MongoRepository."""
        self._server = Config().get('dbserver')
        self._port = Config().get('dbport')

        """
        In MongoDB there are databases, collections and documents.
        
        Databases are well, databases, collections are analogous to tables
        in relational databases and documents hold the actual data.
        
        We will create one database for our application
        and two collections, one which holds complete
        information and one which holds incomplete information.
        
        https://docs.mongodb.com/manual/core/databases-and-collections/
        
        the data is then accessed conveniently:
        tamandua.complete.find( ... )
        very nice and logical.
        """

        self._client = MongoClient(self._server, self._port)

        self._database = self._client[Config().get('database_name')]

        self._collection_complete = self._database[Config().get('collection_complete')]
        self._collection_incomplete = self._database[Config().get('collection_incomplete')]
        self._collection_metadata = self._database[Config().get('collection_metadata')]

    @classmethod
    def _make_regexp(cls, pattern: str, caseSensitive: True) -> object:
        """Make a mongodb regex search value."""
        query = {'$regex': pattern}
        if caseSensitive:
            query['$options'] = '-i'

        return query

    @classmethod
    def _make_comparison(cls, key: str, value: object, comparator: Comparator) -> object:
        """
        Make a mongodb comparator value.

        For example:

        obj1.key >= obj2.key
        turn into:
        {'key': {'$gte': 'value'}}
        """

        if comparator.is_regex():
            if not isinstance(value, str):
                comparator.comparator = Comparator.equal
            else:
                return {
                    key: cls._make_regexp(value, comparator.is_regex_case_insensitive())
                }

        if comparator.comparator == Comparator.not_equal and isinstance(value, str):                        tmp = re.compile(value, re.I)
        else:
            tmp = value

        return {
            key: {
                cls.__comparatorMap[comparator.comparator]: tmp
            }
        }

    @classmethod
    def _make_datetime_comparison(cls, start: datetime, end: datetime) -> object:
        """Make a datetime comparison mongodb search value."""

        obj = {}

        if start is not None:
            tmp = cls._make_comparison('dt', start, Comparator(Comparator.greater))
            obj.update(tmp['dt'])

        if end is not None:
            tmp = cls._make_comparison('dt', end, Comparator(Comparator.less))
            obj.update(tmp['dt'])

        return obj

    @classmethod
    def _parse_expression(cls, expression: Expression) -> dict:
        """Compile a given intermediate expression into a mongodb specific query."""

        target = {}
        isDateTimeSearch = expression.datetime.start is not None or expression.datetime.end is not None

        for f in expression.fields:
            if target.get('$and') is None:
                target['$and'] = []

            key = f.key
            value = f.value
            comparator = Comparator(f.comparator)

            try:
                value = literal_eval(value)
            except Exception as e:
                # It is probably a string or another non primitive type
                pass

            tmp = cls._make_comparison(key, value, comparator)
            target['$and'].append({key: tmp[key]})

        if isDateTimeSearch:
            target['$or'] = []

            for t in get_all_times():
                target['$or'].append({
                    t: cls._make_datetime_comparison(expression.datetime.start, expression.datetime.end)
                })

        return target

    @staticmethod
    def get_config_fields() -> List[str]:
        return ['database_name', 'collection_complete', 'collection_incomplete', 'collection_metadata', 'dbserver', 'dbport']

    def __resolveScope(self, scope: SearchScope):
        """Resolve a given scope to a target collection."""

        if scope == SearchScope.COMPLETE:
            return self._collection_complete
        elif scope == SearchScope.INCOMPLETE:
            return self._collection_incomplete
        elif scope == SearchScope.ALL:
            class CollectionAggregate():
                """
                The purpose of this calls is to operate on
                multiple collection the same way as on a single collection.

                Although only the absolute required methods are implemented.
                """

                @staticmethod
                def find(query: dict) -> CountableIterator[Dict]:
                    complete = self._collection_complete.find(query)
                    incomplete = self._collection_incomplete.find(query)

                    count = complete.count() + incomplete.count()

                    # ultra dirty monkey patching ....
                    # TODO: Do not use reflection to add a method ...
                    # The goal of CollectionAggregate is to provide a
                    # uniform way for accessing multiple collections
                    # (same as single collection)
                    # at the same time. Though this should be refactored
                    # and implemented in a cleaner way

                    c = CountableIterator(
                        itertools.chain(
                            complete,
                            incomplete
                        ),
                        lambda x: count
                    )

                    setattr(c, 'count', lambda: count)

                    return c

                @staticmethod
                def remove(query: dict) -> None:
                    self._collection_complete.remove(query)
                    self._collection_incomplete.remove(query)

            return CollectionAggregate
        else:
            raise TargetCollectionNotFound()

    def find(self, query: Expression, scope: SearchScope) -> CountableIterator[Dict]:
        try:
            searchCollection = self.__resolveScope(scope)
        except TargetCollectionNotFound as e:
            return CountableIterator(iter([]), lambda x: 0)

        q = self._parse_expression(query)
        results = searchCollection.find(q)
        return CountableIterator(results, lambda x: x.count())

    def count_specific_fields(self, query: Expression) -> CountableIterator:
        fieldExp = '$' + query.advcount.field

        if query.advcount.sep is not None:
            groupExp = {'$arrayElemAt':
                             [
                                 {'$split':
                                      [fieldExp, '@']
                                 }, 1
                             ]
                        }
        else:
            groupExp = fieldExp

        pipline = [
            {'$match': self._parse_expression(query)},
            {'$project':
                 {query.advcount.field: fieldExp}
             },
            {'$unwind': fieldExp},
            {'$group':
                 {'_id': groupExp,
                  'value': {'$sum': 1}}
                 },
            {'$group':
                 {'_id': None,
                  'sum': {'$sum': '$value'},
                  'details': {
                      '$push': {'field': '$_id',
                                'value': '$value'}
                                }
                  }
             },
            {'$unwind': '$details'},
            {'$sort': {'details.value': -1}}
        ]

        try:
            return MongoCountSpecificIterable(
                    self._collection_complete.aggregate(pipline)
                )
        except pymongo_errors.OperationFailure as e:
            return CountableIterator(iter([]), lambda x: 0)

    def insert_or_update(self, data: dict, scope: SearchScope) -> None:
        if scope == SearchScope.ALL:
            # we do not support inserting or updating multiple
            # collections at the same time
            raise NotImplementedError()
        
        collection = self.__resolveScope(scope)

        if data.get('_id') is not None:
            collection.update({
                '_id': data['_id']
            }, data)
        else:
            collection.insert_one(data)

    def delete(self, query: Expression, scope: SearchScope) -> None:
        collection = self.__resolveScope(scope)
        collection.remove(self._parse_expression(query))

    def remove_metadata(self, data: dict) -> None:
        try:
            del data['_id']
        except KeyError as e:
            pass


    def __get_metadata(self, field: str) -> dict:
        return self._collection_metadata.find_one({field: {'$exists': True}})


    def __save_metadata(self, field: str, value: object) -> None:
        data = self.__get_metadata(field)

        if data is None:
            self._collection_metadata.insert_one({field: value})
        else:
            data[field] = value
            self._collection_metadata.update({'_id': data['_id']}, data)

    def __get_metadata_wrapp(self, field: str, default: object) -> object:
        data = self.__get_metadata(field)
        if data is None:
            return default
        else:
            return data[field]

    def save_position_of_last_read_byte(self, pos: int) -> None:
        self.__save_metadata(self.__lastBytePosName, pos)

    def get_position_of_last_read_byte(self) -> int:
        return self.__get_metadata_wrapp(self.__lastBytePosName, 0)


    def save_size_of_last_logfile(self, size: int) -> None:
        self.__save_metadata(self.__lastLogfileSizeName, size)

    def get_size_of_last_logfile(self) -> int:
        return self.__get_metadata_wrapp(self.__lastLogfileSizeName, 0)

    def get_all_keys(self) -> List[str]:
        try:
            result = self._collection_complete.map_reduce(
                Code(Loader.load_js('mongo_js.mapper')),
                Code(Loader.load_js('mongo_js.reducer')),
                "results"
            )
        except pymongo_errors.OperationFailure as e:
            return []

        res = result.distinct('_id')
        try:
            res.remove('_id')
        except Exception as e:
            pass

        return res

    def __group_field_values(self,
                             field: str,
                             collection: PyMongoCollection,
                             limit: int = 0,
                             separator: str = None,
                             separatorResultPos: int = 0) -> List[str]:
        if isinstance(separator, str):
            groupExp = {'$arrayElemAt':
                [
                    {'$split':
                         ['$field', separator]
                     }, separatorResultPos
                ]
            }
        else:
            groupExp = '$field'

        pipeline = [
            {'$project': {'field': '$' + field}},
            {'$unwind': '$field'},
            {'$group':
                {'_id': groupExp}
            },
            {'$project': {'field': '$_id'}},
            {'$unwind': '$field'},
        ]

        if limit > 0:
            pipeline.append({'$limit': limit})

        return [x['field'] for x in collection.aggregate(pipeline)]


    def get_choices_for_field(self,
                              field: str,
                              limit: int,
                              separator: str = None,
                              separatorResultPos: int = 0) -> List[str]:
        query = partial(self.__group_field_values,
                        field=field,
                        limit=limit,
                        separator=separator,
                        separatorResultPos=separatorResultPos)

        resultsComplete = query(collection=self._collection_complete)
        resultsIncomplete = query(collection=self._collection_incomplete)

        return list(set().union(resultsComplete,resultsIncomplete))

    def get_all_tags(self) -> List[str]:
        query = partial(self.__group_field_values,
                        field='tags')

        tagsComplete = query(collection=self._collection_complete)
        tagsIncomplete = query(collection=self._collection_incomplete)

        return list(set().union(tagsComplete, tagsIncomplete))

    def save_time_of_last_run(self, dt: datetime):
        self.__save_metadata(self.__lastRunDateTimeName, dt)

    def create_indexes(self, indexes: List[str]) -> None:
        indexModels = []

        # build IndexModels
        for index in indexes:
            indexModels.append(
                IndexModel(
                    [(index, ASCENDING)]
                )
            )

        for collection in (self._collection_complete, self._collection_incomplete):
            collection.create_indexes(indexModels)