#!/usr/bin/env python3

"""
Tamandua. Aggregate information from logfiles.

This is the main (entry point) of the parser.
"""

import os
import sys
import argparse
from json import JSONDecodeError

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from lib.plugin_manager import PluginManager
from lib.config import Config
from lib.serialization.serializer import Serializer


CONFIGFILE = 'config.json'


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
        dest="configfile",
        default=os.path.join(BASEDIR, CONFIGFILE),
        type=str,
        help='Path to the configfile')
    args = parser.parse_args()

    try:
        config = Config(args.configfile)
    except FileNotFoundError as e:
        print('ERROR: configfile "' + args.configfile + '" does not exists.')
        sys.exit(6)
    except JSONDecodeError as e:
        print('There is a syntax error in your config:')
        print(e)
        sys.exit(7)
    except Exception as e:
        print(e)
        sys.exit(8)

    try:
        pluginManager = PluginManager(
            absPluginsPath=os.path.join(BASEDIR, 'plugins-enabled'),
            config=config)
    except Exception as e:
        print(e)
        sys.exit(1)

    for logfile in args.files:
        with open(logfile, 'r') as f:
            try:
                for line in f:
                    pluginManager.process_line(line)
            except UnicodeDecodeError as e:
                print('WARNING: The encoding of ' + logfile + ' could not be determined')
                print(logfile + ' will be (partially) omitted')
                print(e)
                print('\n')
                continue
            except Exception as e:
                print('ERROR:')
                print(e)
                sys.exit(9)

    # print data to stdout
    for container in pluginManager.dataReceiver.containers:
        container.represent()
        print('-' * 60)\

    # serialize data
    serializer = Serializer(config)
    serializer.store(pluginManager.dataReceiver)
        
"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
