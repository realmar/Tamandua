#!/usr/bin/env python3

"""Tamandua Manager provides administrative tools."""


import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

"""
source:   https://github.com/Birdback/manage.py
see also: requirements_manager.txt
"""
from manager import Manager
from src.repository.factory import RepositoryFactory
from src.repository.misc import SearchScope
from src.config import Config
from src.constants import CONFIGFILE


Config().setup(
    os.path.join(BASEDIR, CONFIGFILE),
    BASEDIR
)

manager = Manager()


@manager.command
def reset_last_logfile_pos():
    """Reset the reader position of the logfile to 0."""
    RepositoryFactory()                     \
        .create_repository()                \
        .save_position_of_last_read_byte(0)

    print('Reset last logfile position to 0 successful.')


@manager.command
def remove_incomplete():
    """Delete all incomplete data."""
    RepositoryFactory().create_repository().delete({}, SearchScope.INCOMPLETE)
    print('Successfully deleted all incomplete data.')


@manager.command
def remove_complete():
    """Delete all complete data."""
    RepositoryFactory().create_repository().delete({}, SearchScope.COMPLETE)
    print('Successfully deleted all complete data.')


if __name__ == '__main__':
    manager.main()