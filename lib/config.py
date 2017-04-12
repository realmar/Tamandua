"""Config model."""

import json
from .exceptions import MissingConfigField

class Config():
    """Store and validate the tamandua config."""

    def __init__(self, configpath):
        """Load config as YAML into memory."""
        with open(configpath, 'r') as f:
            self.__config = json.load(f)

        self.__validate()

    def __validate(self):
        """Validate the config and raise exceptions."""
        if self.__config.get('preregex') is None:
            raise MissingConfigField('preregex')

    def get(self, key):
        """Get a config attribute."""
        return self.__config.get(key)
