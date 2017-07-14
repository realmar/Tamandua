"""Module which contains the RepositoryFactory."""

from typing import List


from .mongo import MongoRepository
from .interfaces import IRepository
from .. import config


class RepoNotFound(Exception):
    """
    Thrown when the requested concrete repository
    was not found.
    """

    pass


class RepositoryFactory():
    """
    Factory which uses a factory method to construct a
    concrete repository.

    If you need to use a repository _always_ construct
    it over this factory. (In order to keep the abstraction,
    needed when a change of the storage backend is required.)
    """

    """
    dict with all available repositories, the concrete repository
    is specified in the configfile at the 'database_type' field
    The key of this dict has to match the value of the 'database_type'
    field in the configfile.
    """
    __repo_map = {
        'mongo': {
            'config': MongoRepository.get_config_fields(),
            'cls': MongoRepository
        }
    }

    @classmethod
    def get_required_config_parameters(cls, repo: str) -> List[str]:
        """Return the list of the required config parameters for a given 'repo'."""

        try:
            return cls.__repo_map[repo]['config']
        except KeyError as e:
            raise RepoNotFound()

    @classmethod
    def get_available_repositories(cls) -> List[str]:
        """Get a list of the names of all available repositories."""

        return list(cls.__repo_map.keys())

    @classmethod
    def create_repository(cls) -> IRepository:
        """
        Create the instance of the concrete repository specified in the
        configfile 'database_type' field.
        """

        try:
            return cls.__repo_map[config.Config().get('database_type')]['cls']()
        except KeyError as e:
            raise RepoNotFound()