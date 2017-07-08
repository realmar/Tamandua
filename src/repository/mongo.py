"""Module which contains the repository implementation for mongodb."""


import itertools
from pymongo import MongoClient
import pymongo.errors as pymongo_errors

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
    pass


class MongoCountSpecificIterable(CountableIterator):
    """"""

    def __init__(self, cursor):
        self.__cursor = cursor

    def __next__(self):
        x = next(self.__cursor)
        while x['_id'] == '' or x['_id'] == None:
            x = next(self.__cursor)

        return {'key': x['_id'], 'value': x['value']}

    def __len__(self):
        return self.__cursor.count()

class MongoRepository(IRepository):
    """"""

    __lastBytePosName = 'lastbytepos'
    __lastLogfileSizeName = 'lastlogfilesize'
    __lastRunDateTimeName = 'lastrundatetime'


    def __init__(self):
        """"""
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
        """"""
        query = {'$regex': pattern}
        if not caseSensitive:
            query['$options'] = '-i'

        return query

    @classmethod
    def _make_comparison(cls, key: str, value: object, comparator: Comparator) -> object:
        """"""
        comparatorMap = {
            Comparator.equal: '$eq',
            Comparator.not_equal: '$ne',
            Comparator.greater: '$gt',
            Comparator.less: '$lt',
            Comparator.greater_or_equal: '$gte',
            Comparator.less_or_equal: '$lte'
        }

        return {
            key: {
                comparatorMap[comparator.comparator]: value
            }
        }

    @classmethod
    def _make_datetime_comparison(cls, start: datetime, end: datetime) -> object:
        """"""
        obj = {}

        if start is not None:
            tmp = cls._make_comparison('dt', start, Comparator(Comparator.greater))
            obj.update(tmp['dt'])

        if end is not None:
            tmp = cls._make_comparison('dt', start, Comparator(Comparator.less))
            obj.update(tmp['dt'])

        return obj

    @classmethod
    def _parse_expression(cls, expression: Expression) -> dict:
        target = {}
        isDateTimeSearch = expression.datetime.start is not None or expression.datetime.end is not None

        for f in expression.fields:
            for k, v in f.items():
                value = v['value']
                comparator = Comparator(v['comparator'])

                try:
                    value = literal_eval(value)
                except Exception as e:
                    pass

                if comparator.comparator == Comparator.equal:
                    if isinstance(value, str):
                        tmp = cls._make_regexp(value, caseSensitive=False)
                    else:
                        tmp = value

                    if target.get(k) is not None:
                        target[k].update(tmp)
                    else:
                        target[k] = tmp
                else:
                    tmp = cls._make_comparison(k, value, comparator)
                    if target.get(k) is not None:
                        target[k].update(tmp[k])
                    else:
                        target[k] = tmp[k]

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
        if scope == SearchScope.COMPLETE:
            return self._collection_complete
        elif scope == SearchScope.INCOMPLETE:
            return self._collection_incomplete
        elif scope == SearchScope.ALL:
            class CollectionAggregate():
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
        """"""
        try:
            searchCollection = self.__resolveScope(scope)
        except TargetCollectionNotFound as e:
            return CountableIterator(iter([]), lambda x: 0)

        results = searchCollection.find(self._parse_expression(query))
        return CountableIterator(results, lambda x: x.count())

    def count_specific_fields(self, query: Expression, field: str, regex=None) -> CountableIterator:
        """"""
        mapf = Loader.load_js('mongo_js.count.mapper')
        reducef = Loader.load_js('mongo_js.count.reducer')

        mapf = mapf.replace('<field>', field)
        if regex is not None:
            mapf = mapf.replace('<regex>', '.match(/' + regex + '/)[1]')
        else:
            mapf = mapf.replace('<regex>', '')

        try:
            results = self._collection_complete.map_reduce(
                Code(mapf), Code(reducef), "count", query=self._parse_expression(query)
            )
        except pymongo_errors.OperationFailure as e:
            return CountableIterator(iter([]), lambda x: 0)

        return MongoCountSpecificIterable(results.find({}).sort('value', -1))

    def insert_or_update(self, data: dict, scope: SearchScope) -> None:
        """"""
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
        """"""
        collection = self.__resolveScope(scope)
        collection.remove(self._parse_expression(query))

    def remove_metadata(self, data: dict) -> None:
        """"""
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
        """"""
        self.__save_metadata(self.__lastBytePosName, pos)

    def get_position_of_last_read_byte(self) -> int:
        """"""
        return self.__get_metadata_wrapp(self.__lastBytePosName, 0)


    def save_size_of_last_logfile(self, size: int) -> None:
        """"""
        self.__save_metadata(self.__lastLogfileSizeName, size)

    def get_size_of_last_logfile(self) -> int:
        """"""
        return self.__get_metadata_wrapp(self.__lastLogfileSizeName, 0)

    def get_all_keys(self) -> List[str]:
        """"""
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

    def get_all_tags(self) -> List[str]:
        """"""
        targetCollections = [
            self._collection_complete,
            self._collection_incomplete
        ]

        result = set()

        for tc in targetCollections:
            try:
                result.update(list(tc.map_reduce(
                    Code(Loader.load_js('mongo_js.tags_mapper')),
                    Code(Loader.load_js('mongo_js.reducer')),
                    "results"
                ).distinct('_id')))
            except pymongo_errors.OperationFailure as e:
                return []

        return list(result)

    def save_time_of_last_run(self, dt: datetime):
        """"""
        self.__save_metadata(self.__lastRunDateTimeName, dt)