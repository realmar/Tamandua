#!/usr/bin/env python3

"""Tamandua Manager provides administrative tools."""


import os
import sys
import atexit

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

"""
source:   https://github.com/Birdback/manage.py
see also: requirements_manager.txt
"""
from manager import Manager
from datetime import datetime, timedelta
import subprocess

from src.repository.factory import RepositoryFactory
from src.repository.misc import SearchScope
from src.config import Config
from src.constants import CONFIGFILE, PHD_MXIN_TIME, PHD_IMAP_TIME
from src.expression.builder import ExpressionBuilder, Comparator


Config().setup(
    os.path.join(BASEDIR, CONFIGFILE),
    BASEDIR
)

pidfile = os.path.join(BASEDIR, 'tamandua.pid')

manager = Manager()

global cleanupPID
cleanupPID = True


def exit_if_already_running():
    if os.path.exists(pidfile):
        print('There is already a tamandua process running. Exiting.')
        global cleanupPID
        cleanupPID = False
        sys.exit(1)

    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))


@atexit.register
def remove_pid():
    global cleanupPID
    if cleanupPID:
        os.remove(pidfile)

    try:
        os.remove(os.path.join(BASEDIR, 'logfile'))
    except FileNotFoundError as e:
        pass


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


@manager.arg('days', help='Number of days to keep')
@manager.command
def cleanup(days=30):
    """Deletes entries which are older than n days."""
    repository = RepositoryFactory.create_repository()
    keepDate = datetime.today() - timedelta(days=days)

    builder = ExpressionBuilder().set_end_datetime(keepDate)

    repository.delete(builder.expression, SearchScope.ALL)

    print('Deleted all data older than ' + str(days) + ' days successful.')


def run_remotesshwrapper_command(command: str, args: list=[], stdout: object=subprocess.PIPE) -> subprocess.Popen:
    return subprocess.Popen(
        [
            'ssh',
            '-o',
            'IdentitiesOnly=yes',
            '-i',
            '~/.ssh/remotesshwrapper',
            'root@phd-systemxen',
            '/usr/local/bin/remotesshwrapper',
            command,
            ' '.join(args)
        ],
        stdout=stdout
    )


@manager.command
def run():
    """Get logfile and run the parser. This can be used within cronjobs."""
    repository = RepositoryFactory.create_repository()

    logfilename = os.path.join(BASEDIR, 'logfile')
    lastlogfilesize = repository.get_size_of_last_logfile()

    process = run_remotesshwrapper_command('getmaillogsize')
    currlogfilesize = int(process.communicate()[0].decode('utf-8'))

    print('Last logfile size: %d' % lastlogfilesize)
    print('Current logfile size: %d' % currlogfilesize)

    if currlogfilesize < lastlogfilesize:
        print('New logfile detected, reading from beginning.')
        logfile_pos()

    repository.save_size_of_last_logfile(currlogfilesize)
    currByte = repository.get_position_of_last_read_byte()

    print('Position of last read byte: %d' % currByte)

    with open(logfilename, 'wb') as f:
        print('Start transferring logfile diff to local machine\n')
        process = run_remotesshwrapper_command('tamandua', args=[str(max(0, currByte - 1000))], stdout=f)
        process.wait()

    from tamandua_parser import main as tamandua_main
    from tamandua_parser import DefaultArgs

    args = DefaultArgs()
    args.logfile = logfilename
    args.noprint = True

    print('\nStart reading the logfile')

    tamandua_main(args)
    cleanup()

    repository.save_time_of_last_run(datetime.now())

    os.remove(logfilename)


if __name__ == '__main__':
    exit_if_already_running()
    manager.main()