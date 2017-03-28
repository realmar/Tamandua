#!/usr/bin/env python3

"""
Statlyser. Generate statistics out of information from logfiles.

This is the main (entry point) of the application.
"""

import os
import sys
import argparse
from json import JSONDecodeError

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from lib.plugin_manager import PluginManager
from lib.config import Config
from lib.exceptions import NoSubscriptionRegex, NoDataRegex, RegexGroupsMissing, MissingConfigField


CONFIGFILE = 'statlyser.json'


def main():
    """Entry point of the application."""
    parser = argparse.ArgumentParser(
        description="Statlyser generates statistics from logfile data")
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
    except MissingConfigField as e:
        print(e)
        sys.exit(8)

    try:
        pluginManager = PluginManager(
            absPluginsPath=os.path.join(BASEDIR, 'plugins-enabled'),
            config=config)
    except NoSubscriptionRegex as e:
        print(e)
        sys.exit(1)
    except NoDataRegex as e:
        print(e)
        sys.exit(2)
    except RegexGroupsMissing as e:
        print(e)
        sys.exit(3)

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

    # output the statistics to STDOUT
    pluginManager.statistics.represent()


"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
