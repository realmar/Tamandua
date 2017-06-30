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

pidfile = os.path.join(BASEDIR, 'tamandua.pid')

manager = Manager()


def exit_if_already_running():
    if os.path.exists(pidfile):
        print('There is already a tamandua process running. Exiting.')
        sys.exit(1)

    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid():
    os.remove(pidfile)


@manager.command(namespace='reset')
def logfile_pos():
    """Reset the reader position of the logfile to 0."""
    RepositoryFactory                       \
        .create_repository()                \
        .save_position_of_last_read_byte(0)

    print('Reset last logfile position to 0 successful.')


@manager.command(namespace='reset')
def logfile_size():
    """Reset the last size of the logfile to 0."""
    RepositoryFactory                       \
        .create_repository()                \
        .save_size_of_last_logfile(0)

    print('Reset last logfile size to 0 successful.')


@manager.command(namespace='remove')
def incomplete():
    """Delete all incomplete data."""
    RepositoryFactory                       \
        .create_repository()                \
        .delete({}, SearchScope.INCOMPLETE)

    print('Successfully deleted all incomplete data.')


@manager.command(namespace='remove')
def complete():
    """Delete all complete data."""
    RepositoryFactory                       \
        .create_repository()                \
        .delete({}, SearchScope.COMPLETE)

    print('Successfully deleted all complete data.')


@manager.command(namespace='remove')
def all():
    """Delete all data from the database and reset the reader position."""
    complete()
    incomplete()
    logfile_pos()
    logfile_size()


@manager.command
def cleanup():
    """Deletes entries which are older than n days."""
    pass


@manager.command
def run():
    """Get logfile and run the parser. This can be used within cronjobs."""
    repository = RepositoryFactory.create_repository()

    logfilename = os.path.join(BASEDIR, 'logfile')
    lastlogfilesize = repository.get_size_of_last_logfile()

    import subprocess
    with open(logfilename, 'wb') as f:
        process = subprocess.Popen(
            [
                'ssh',
                '-o',
                'IdentitiesOnly=yes',
                '-i',
                '~/.ssh/remotesshwrapper',
                'root@phd-systemxen',
                '/usr/local/bin/remotesshwrapper',
                'tamandua'
            ],
            stdout=f
        )
        process.wait()

    currlogfilesize = os.path.getsize(logfilename)
    if currlogfilesize < lastlogfilesize:
        print('New logfile detected, reading from beginning.')
        logfile_pos()

    repository.save_size_of_last_logfile(currlogfilesize)

    from tamandua_parser import main as tamandua_main
    from tamandua_parser import DefaultArgs

    args = DefaultArgs()
    args.logfile = logfilename
    args.noprint = True

    tamandua_main(args)

    os.remove(logfilename)


if __name__ == '__main__':
    exit_if_already_running()
    manager.main()
    remove_pid()