"""Config model."""

import json
from .exceptions import MissingConfigField, InvalidConfigField
from  .repository import factory as repofactory
from .singleton import Singleton

class Config(metaclass=Singleton):
    """Store and validate the tamandua config."""

    def __init__(self):
        self.__config = {}

    def setup(self, configpath: str, basepath: str, overwrite: dict = None):
        """Load config as YAML into memory."""
        with open(configpath, 'r') as f:
            self.__config = json.load(f)

        if isinstance(overwrite, dict):
            for k, v in overwrite.items():
                if v is not None:
                    self.__config[k] = v

        self.__validate()
        self.__config['basepath'] = basepath

    def __validate(self) -> None:
        """Validate the config and raise exceptions."""

        requiredConfigFields = ['preregex', 'database_type']

        if not isinstance(self.__config.get('limit_hosts'), list):
            self.__config['limit_hosts'] = []

        try:
            repo_config_params = repofactory.RepositoryFactory.get_required_config_parameters(
                self.__config['database_type']
            )
            requiredConfigFields.extend(repo_config_params)
        except repofactory.RepoNotFound as e:
            raise InvalidConfigField('database_type',
                                     str(repofactory.RepositoryFactory.get_available_repositories())
                                     )
        except KeyError as e:
            raise MissingConfigField('database_type')

        for name in requiredConfigFields:
            if self.__config.get(name) is None:
                raise MissingConfigField(name)

    def get(self, key: str) -> object:
        """Get a config attribute."""
        return self.__config.get(key)
