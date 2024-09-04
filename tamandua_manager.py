#!/usr/bin/env python3

"""Tamandua Manager provides administrative tools."""


import os
import sys
import atexit

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

if True: # noqa: E402
    import click
    from datetime import datetime, timedelta
    import subprocess

    from src.repository.factory import RepositoryFactory
    from src.repository.misc import SearchScope
    from src.config import Config
    from src.constants import CONFIGFILE
    from src.expression.builder import ExpressionBuilder


Config().setup(
    os.path.join(BASEDIR, CONFIGFILE),
    BASEDIR
)

pidfile = os.path.join(BASEDIR, 'tamandua.pid')

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


def run_remotesshwrapper_command(
    command: str, args: list = [], stdout: object = subprocess.PIPE
) -> subprocess.Popen:
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


@atexit.register
def remove_pid():
    global cleanupPID
    if cleanupPID:
        os.remove(pidfile)

    try:
        os.remove(os.path.join(BASEDIR, 'logfile'))
    except FileNotFoundError:
        pass


@click.group()
def cli():
    """Tamandua manager with admin tools."""
    pass


@cli.command()
def reset_logfile_pos():
    """Reset the reader position of the logfile to 0."""
    RepositoryFactory                       \
        .create_repository()                \
        .save_position_of_last_read_byte(0)

    print('Reset last logfile position to 0 successful.')


@cli.command()
def reset_logfile_size():
    """Reset the last size of the logfile to 0."""
    RepositoryFactory                       \
        .create_repository()                \
        .save_size_of_last_logfile(0)

    print('Reset last logfile size to 0 successful.')


@cli.command()
def remove_incomplete():
    """Delete all incomplete data."""
    RepositoryFactory                       \
        .create_repository()                \
        .delete({}, SearchScope.INCOMPLETE)

    print('Successfully deleted all incomplete data.')


@cli.command()
def remove_complete():
    """Delete all complete data."""
    RepositoryFactory                       \
        .create_repository()                \
        .delete({}, SearchScope.COMPLETE)

    print('Successfully deleted all complete data.')


@cli.command()
@click.pass_context
def remove_all(ctx):
    """Delete all data and reset the reader position."""
    ctx.invoke(remove_complete)
    ctx.invoke(remove_incomplete)
    ctx.invoke(reset_logfile_pos)
    ctx.invoke(reset_logfile_size)


@cli.command()
def cache_document_keys():
    """Build cache with all distinct keys of documents."""
    RepositoryFactory                   \
        .create_repository()            \
        .get_all_keys(True)

    print('Successfully built cache of unique document keys.')


@cli.command()
@click.option('--days', help='Number of days to keep', default=30, show_default=True)
def cleanup(days):
    """Deletes entries which are older than n days."""
    repository = RepositoryFactory.create_repository()
    keepDate = datetime.today() - timedelta(days=days)

    builder = ExpressionBuilder().set_end_datetime(keepDate)

    repository.delete(builder.expression, SearchScope.ALL)

    print('Deleted all data older than ' + str(days) + ' days successful.')


@cli.command()
@click.pass_context
def run(ctx):
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
        ctx.invoke(reset_logfile_pos)

    repository.save_size_of_last_logfile(currlogfilesize)
    currByte = repository.get_position_of_last_read_byte()

    print('Position of last read byte: %d' % currByte)

    if currlogfilesize < currByte:
        print('Logfile is smaller than last position, reading from beginning.')
        ctx.invoke(reset_logfile_pos)
        currByte = 0

    with open(logfilename, 'wb') as f:
        print('Start transferring logfile diff to local machine\n')
        process = run_remotesshwrapper_command('tamandua', args=[str(currByte)], stdout=f)
        process.wait()

    from tamandua_parser import main as tamandua_main
    from tamandua_parser import DefaultArgs

    args = DefaultArgs()
    args.logfile = logfilename
    args.printmsgs = True

    print('\nStart reading the logfile')

    tamandua_main(args)
    ctx.invoke(cleanup)

    repository.save_time_of_last_run(datetime.now())

    os.remove(logfilename)


if __name__ == '__main__':
    exit_if_already_running()
    cli()
