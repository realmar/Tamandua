"""Module with a serialization methods available."""

import json
import pickle

from ..interfaces import ISerializationMethod


class BaseSerialization(ISerializationMethod):
    def __init__(self, path):
        self.path = path


class JSONSerialization(BaseSerialization):
    def save(self, data: object) -> None:
        """Serialize data."""
        with open(self.path, 'w') as f:
            json.dump(data, f)

    def load(self) -> object:
        """Deserialize data and return it."""
        with open(self.path, 'r') as f:
            return json.load(f)


class PickleSerialization(BaseSerialization):
    def save(self, data: object) -> None:
        """Serialize data."""
        with open(self.path, 'wb') as f:
            pickle.dump(data, f)

    def load(self) -> object:
        """Deserialize data and return it."""
        with open(self.path, 'rb') as f:
            return pickle.load(f)