"""Module which contains the repository implementation for mongodb."""


from pymongo import MongoClient
from bson.code import Code
from datetime import datetime

from typing import List, Dict, Tuple
from .interfaces import IRepository
from .misc import SearchScope
from .js import Loader
from ..config import Config
from ..constants import TIME_FORMAT


class TargetCollectionNotFound(Exception):
    pass


class MongoRepository(IRepository):
    """"""

    __lastBytePosName = 'lastbytepos'


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
                def find(query: dict):
                    res = list(
                        self._collection_complete.find(query))

                    res.extend(
                        list(
                            self._collection_incomplete.find(query)))

                    return res

            return CollectionAggregate
        else:
            raise TargetCollectionNotFound()

    def find(self, query: dict, scope: SearchScope) -> List[Dict]:
        """"""
        try:
            searchCollection = self.__resolveScope(scope)
        except TargetCollectionNotFound as e:
            return []

        results = searchCollection.find(query)
        return list(results)

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

    def delete(self, query: dict, scope: SearchScope) -> None:
        """"""
        if scope == SearchScope.ALL:
            # we do not support deleting the same document
            # in multiple collections at the same time
            raise NotImplementedError()

        collection = self.__resolveScope(scope)
        collection.remove(query)

    def remove_metadata(self, data: dict) -> None:
        """"""
        try:
            del data['_id']
        except KeyError as e:
            pass

    def __get_last_bypte_post_cursor(self) -> dict:
        return self._collection_metadata.find_one({self.__lastBytePosName: {'$exists': True}})

    def save_position_of_last_read_byte(self, pos: int) -> None:
        """"""
        lastpos = self.__get_last_bypte_post_cursor()
        if lastpos is None:
            self._collection_metadata.insert_one({self.__lastBytePosName: pos})
        else:
            lastpos[self.__lastBytePosName] = pos
            self._collection_metadata.update({'_id': lastpos['_id']}, lastpos)

    def get_position_of_last_read_byte(self) -> int:
        """"""
        lastpos = self.__get_last_bypte_post_cursor()
        if lastpos is None:
            return 0
        else:
            return lastpos[self.__lastBytePosName]

    def make_regexp(self, pattern: str) -> object:
        """"""
        return {'$regex': pattern}

    def make_datetime_comparison(self, start: datetime, end: datetime) -> object:
        """"""

        obj = {}

        if start is not None:
            obj['$gte'] = start

        if end is not None:
            obj['$lte'] = end

        return obj

    def get_all_keys(self) -> List[str]:
        """"""
        result = self._collection_complete.map_reduce(
            Code(Loader.load_js('mongo_js.mapper')),
            Code(Loader.load_js('mongo_js.reducer')),
            "results"
        )

        return result.distinct('_id')