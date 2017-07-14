"""This Module contains all interfaces used for the repository."""

from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict
from datetime import datetime

from .misc import SearchScope, CountableIterator
from ..expression.builder import Expression


class IRepository(metaclass=ABCMeta):
    """
    Interface which represents all repositories. (repository pattern)

    Each repository has to implement this interface and represents one storage
    backend. Eg. MongoDB, MySQL.

    All code requiring access to a storage backend has to do this over a
    concrete repository. (Not directly use the library of the storage backend)

    Generally speaking a repository will implement the CRUD pattern in some way.
    """

    @staticmethod
    @abstractmethod
    def get_config_fields() -> List[str]:
        """
        Return a list of all required config fields for this concrete repository.

        For Example:
        If you return:

        return ['servername', 'databasename']

        Then the user will be required to provide these two config fields
        if they choose that concrete repository.

        {
            "servername": "localhost",
            "databasename": "tamandua"
        }

        This logic is enforced by the src.config.Config class.
        """
        pass

    @abstractmethod
    def find(self, query: Expression, scope: SearchScope) -> CountableIterator[Dict]:
        """
        R: Read

        Take a given query and perform a search operation on the storage backend
        following the contraints given by the query.

        The query is of type Expression, meaning that it is using tamandua's own
        intermediate query language. So you will not be able to directly give this query
        to the storage backend but first need to compile it into the concrete
        query required by the given storage backend.

        Return a CountableIterator as the framework has to be able to count the results.
        This also means that you have to specify how to count the results.

        IMPORTANT: supply each result with some metadata with which
        you can identify that result in the storage backend if the client
        performs some operations on it and supplies it to the insert_or_update
        method for udpate.
        In case of mongodb this is handled by the pymongo drivers, meaning this metadata
        is an additional key called '_id' which represents the primary key
        of that document in the collection.
        """
        pass

    @abstractmethod
    def count_specific_fields(self, query: Expression) -> CountableIterator:
        """
        Count values of a specific field.

        The dashboard in the view shows multiple lists with top occurrences
        of some field. For example the top reject reasons are listed there.
        In order to collect this data the occurrences of each value in the
        rejectreason field has to be counted. That is exactly what this method
        is responsible for.

        You may use map reduce for that:

        map    -> emit: document.rejectreason, 1
        reduce -> sum: key.values

        Although most dbs have more efficient methods.
        """
        pass

    @abstractmethod
    def insert_or_update(self, data: dict, scope: SearchScope) -> None:
        """
        C: Create
        or
        U: Update

        insert new data into the storage backend or update existing data
        which is already stored in the storage backend.

        As argument there is the actual data as a dict and the scope.
        The scope hints in which scope the data should be inserted.
        Eg.: COMPLETE or INCOMPLETE --> in your storage backend there may
        be two databases for those two scopes. (a db for each scope)

        In order to know if the data needs to be updated or inserted
        supply it with some metadata in the find() method. In case of
        mongodb this metadata is an additional key called '_id' which
        stores the primary key of this document. If the client then calls
        insert_or_update and you find this metadata again, you know
        that this data exists already and should only get updated.
        Although you may do it differently, eg. by searching the
        storage backend for the data provided. (Although this is
        discouraged, as the framework also makes use of the remove_metadata
        method)
        """
        pass

    @abstractmethod
    def delete(self, query: Expression, scope: SearchScope) -> None:
        """
        D: Delete

        Delete data from the storage backend according to the constraints
        in the query. The query is in form of Tamandua's intermediate expression
        which means you need to compile it into the concrete query required
        by the given storage backend.

        SearchScope hints in which scope the data should get deleted.
        """
        pass

    @abstractmethod
    def remove_metadata(self, data: dict) -> None:
        """
        Remove metadata from a result set.

        In the find() method you supplied each result with some metadata in order
        to identify it in the insert_or_update method.
        In this method you need to remove this metadata from the result.
        """
        pass

    @abstractmethod
    def save_position_of_last_read_byte(self, pos: int) -> None:
        """
        Save the position of the last read byte in the storage backend.

        Such metadata is usually stored in an additional database called
        metadata. The position of the last byte is important for the parser
        to perform aggregation only on a diff of the logfile.
        """
        pass

    @abstractmethod
    def get_position_of_last_read_byte(self) -> int:
        """
        Return the last read byte in the logfile from the storage backend.
        """
        pass

    @abstractmethod
    def save_size_of_last_logfile(self, pos: int) -> None:
        """
        Save the size of the last read logfile.

        This is important for the manager to detect if it is parsing
        a new logfile or if it is still the same logfile.
        """
        pass

    @abstractmethod
    def get_size_of_last_logfile(self) -> int:
        """
        Return the size of the last read logfile from the storage backend.
        """
        pass

    @abstractmethod
    def get_all_keys(self) -> List[str]:
        """
        Return a list of all distinct keys in all stored objects.

        In the search form in the view, you may search all available fields
        in the objects. This method supplies the view with that data. (Which
        keys exists)
        """
        pass

    @abstractmethod
    def get_all_tags(self) -> List[str]:
        """
        Return a list of all tags found in the objects.
        """
        pass

    @abstractmethod
    def save_time_of_last_run(self, dt: datetime):
        """
        Store date and time of the last run in the storage backend.
        (In the metadata database)
        """
        pass

    @abstractmethod
    def get_choices_for_field(self,
                              field: str,
                              limit: int,
                              separator: str = None,
                              separatorResultPos: int = 0) -> List[str]:
        """
        Return a list with all distinct values of a given field.

        This is used in the view to give the user a choice of all available
        values for a given field but only if the count of the available values
        is less than 'limit'

        For example:

        For the field 'action' there are two choices: 'reject' and 'hold'
        return a list with those two values.
        """
        pass


    @abstractmethod
    def create_indexes(self, indexes: List[str]) -> None:
        """
        Create all indexes given in the 'indexes' arg in the storage backend.
        """
        pass