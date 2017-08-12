"""Module which contains caching facilities."""

from datetime import datetime
from typing import Generic, TypeVar, Callable

T = TypeVar('T')


class DataCache(Generic[T]):
    """Class to cache data retrieved by a query."""

    def __init__(self, dataFunc: Callable[[], T], revalidationInterval: float):
        """Constructor of DataCache."""
        self._dataFunc = dataFunc
        # interval is in seconds
        self._revalidationInterval = revalidationInterval

        self._lastCacheTime = datetime.now()
        self._data = self._get_data(force=True)

    def _get_data(self, force: bool = False) -> T:
        """Validate data, get data and return it."""
        currdt = datetime.now()
        dtdiff = currdt - self._lastCacheTime

        if force or dtdiff.seconds > self._revalidationInterval:
            self._data = self._dataFunc()

        return self._data

    @property
    def data(self) -> T:
        """Data property."""
        return self._get_data()