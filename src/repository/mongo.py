"""Module which contains the repository implementation for mongodb."""


from pymongo import MongoClient

from typing import List, Dict
from .interfaces import IRepository
from .misc import SearchScope
from ..config import Config


class TargetCollectionNotFound(Exception):
    pass


class MongoRepository(IRepository):
    """"""

    def __init__(self, config: Config):
        """"""
        # TODO: this should go into the config
        self._server = 'localhost'
        self._port = 27017

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

        self._dbconfig = {
            'database': 'tamandua',
            'collection_complete': 'complete',
            'collection_incomplete': 'incomplete'
        }

        self._client = MongoClient(self._server, self._port)

        self._database = self._client[self._dbconfig['database']]
        self._collection_complete = self._database[self._dbconfig['collection_complete']]
        self._collection_incomplete = self._database[self._dbconfig['collection_incomplete']]

    def __resolveScope(self, scope: SearchScope):
        if scope == SearchScope.COMPLETE:
            return self._collection_complete
        elif scope == SearchScope.INCOMPLETE:
            return self._collection_incomplete
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
        collection = self.__resolveScope(scope)

        if data.get('_id') is not None:
            collection.update({
                '_id': data['_id']
            }, data)
        else:
            collection.insert_one(data)

    def delete(self, query: dict, scope: SearchScope) -> None:
        """"""
        collection = self.__resolveScope(scope)
        collection.remove(query)