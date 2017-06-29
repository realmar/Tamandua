""""""

from typing import List


from .mongo import MongoRepository
from .interfaces import IRepository
from .. import config


class RepoNotFound(Exception):
    pass


class RepositoryFactory():
    """"""

    __repo_map = {
        'mongo': {
            'config': MongoRepository.get_config_fields(),
            'cls': MongoRepository
        }
    }

    @classmethod
    def get_required_config_parameters(cls, repo: str) -> List[str]:
        try:
            return cls.__repo_map[repo]['config']
        except KeyError as e:
            raise RepoNotFound()

    @classmethod
    def get_available_repositories(cls) -> List[str]:
        return list(cls.__repo_map.keys())

    @classmethod
    def create_repository(cls) -> IRepository:
        try:
            return cls.__repo_map[config.Config().get('database_type')]['cls']()
        except KeyError as e:
            raise RepoNotFound()