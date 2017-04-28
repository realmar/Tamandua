#!/usr/bin/env python3

"""
Tamandua. Aggregate information from logfiles.

This is the main (entry point) of the parser.
"""

import os
import sys
import argparse

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

# JSONDecodeError exists from python 3.5 and onwards
# As Debian Jessie only has python 3.4 we need this workaround
if sys.version_info[1] < 5:
    JSONDecodeError = ValueError
else:
    from json import JSONDecodeError

from lib.plugins.plugin_manager import PluginManager
from lib.config import Config
from lib.serialization.serializer import Serializer
from lib.constants import CONFIGFILE
from lib.exceptions import print_exception


def main():
    """Entry point of the application."""
    parser = argparse.ArgumentParser(
        description="Tamandua parser aggregates from logfile data")
    parser.add_argument(
        'files',
        nargs='+',
        metavar='LOGFILE',
        type=str,
        help='Logfiles to be parsed')
    parser.add_argument(
        '--config',
        '-c',
        dest='configfile',
        default=os.path.join(BASEDIR, CONFIGFILE),
        type=str,
        help='Path to the configfile')
    parser.add_argument(
        '--no-print',
        dest='noprint',
        default=False,
        action='store_true',
        help='Do not print results to stdout')
    args = parser.parse_args()

    try:
        config = Config(args.configfile, BASEDIR)
    except FileNotFoundError as e:
        print_exception(
            e,
            "Trying to read the config",
            "Exiting application",
            description="The configfile was not found",
            fatal=True)
        sys.exit(6)
    except JSONDecodeError as e:
        print_exception(
            e,
            "Trying to parse the config",
            "Exiting application",
            description="Syntax error in the configfile",
            fatal=True)
        print(e)
        sys.exit(7)
    except Exception as e:
        print_exception(e, "Trying to read the config", "Exiting application", fatal=True)
        sys.exit(8)

    try:
        pluginManager = PluginManager(
            absPluginsPath=os.path.join(BASEDIR, 'plugins-enabled'),
            config=config)
    except Exception as e:
        print_exception(
            e,
            "Trying to create an instance of PluginManager",
            "Exiting Application",
            fatal=True)
        sys.exit(1)

    for logfile in args.files:
        with open(logfile, 'r') as f:
            try:
                for line in f:
                    pluginManager.process_line(line)
            except UnicodeDecodeError as e:
                print_exception(
                    e,
                    "Trying to read a line from the given logfile.",
                    "Continue with the next line")
                continue
            except Exception as e:
                print_exception(
                    e,
                    "Trying to read a line from the given logfile",
                    "Quit application",
                    fatal=True)
                sys.exit(9)

    # print data to stdout
    for container in pluginManager.dataReceiver.containers:
        container.build_final()                 # build final data

        if not args.noprint:
            container.represent()                   # represent data
            container.print_integrity_report()      # print integrity stats

            print('\n')
            print('-' * 60)
            print('\n')

    # serialize data
    try:
        serializer = Serializer(config)
    except Exception as e:
        print_exception(e, "Trying to create an instance of Serializer", "Discard serialization")
    else:
        try:
            serializer.store(pluginManager.dataReceiver)
        except Exception as e:
            print_exception(e, "Trying to serialize the collected data", "Discard serialization")
        
"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
