"""
Statlyser. Generate statistics out of information from logfiles.

This is the main (entry point) of the application.
"""

import os
import sys
BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from lib.plugin_manager import PluginManager


def main():
    """Entry point of the application."""
    pluginManager = PluginManager(os.path.join(BASEDIR, 'Plugins'))
    if len(sys.argv) > 2:
        print('ERROR:')
        print('First parameter has to be the logfile.')
        print('Currently only one logfile per run is supported.')

        sys.exit(1)

    logfile = sys.argv[1]

    with open(logfile, 'r') as f:
        line = f.readline()

        while line:
            pluginManager.process_line(line)
            line = f.readline()

    # output the statistic to STDOUT
    pluginManager.statistic.represent()


"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
