#!/usr/bin/env python3

"""
Statlyser. Generate statistics out of information from logfiles.

This is the main (entry point) of the application.
"""

import os
import sys
BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

import argparse

from lib.plugin_manager import PluginManager
from lib.exceptions import NoSubscriptionRegex, NoDataRegex, RegexGroupsMissing


# some hostnames come with the username prepended
# so we have to catch this case
# PREREGEX = r':\d{2} ([^@]*@)?(?P<hostname>[^\/\s]*)'

PREREGEX = r':\d{2} (?P<hostname>[^\/\s]*)'


def main():
    """Entry point of the application."""
    parser = argparse.ArgumentParser(description="Statlyser generates statistics from logfile data")
    parser.add_argument('files', nargs='+', metavar='LOGFILE', type=str, help='Logfiles to be parsed')
    args = parser.parse_args()

    try:
        pluginManager = PluginManager(os.path.join(BASEDIR, 'Plugins'), PREREGEX)
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
