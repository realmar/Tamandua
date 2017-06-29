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

from src.plugins.plugin_manager import PluginManager
from src.config import Config
from src.constants import CONFIGFILE
from src.exceptions import print_exception


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
        '--outpath',
        '-o',
        dest='store_path',
        default=None,
        type=str,
        help='Path to the output file')
    parser.add_argument(
        '--outformat',
        '-f',
        dest='store_type',
        default=None,
        type=str,
        help='Output format: can be either pyobj-store or json')
    parser.add_argument(
        '--no-print',
        dest='noprint',
        default=False,
        action='store_true',
        help='Do not print results to stdout')
    args = parser.parse_args()

    try:
        Config().setup(
            args.configfile,
            BASEDIR,
            {
                'store_path': args.store_path,
                'store_type': args.store_type
            }
        )
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
            absPluginsPath=os.path.join(BASEDIR, 'plugins-available'))
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
        try:
            container.build_final()                 # build final data
        except Exception as e:
            print_exception(
                e,
                'Aggregating the data',
                'Discarding aggregation and exiting application',
                fatal=True)
            sys.exit(10)

        if not args.noprint:
            try:
                container.represent()                   # represent data

                print('\n')
                print('-' * 60)
                print('\n')
            except Exception as e:
                print_exception(
                    e,
                    'Printing container to stdout: ' + container.__class__.__name__,
                    'ignoring current container')

        
"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
