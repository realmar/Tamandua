"""
Statlyser. Generate statistics out of information from logfiles.

This is the main (entry point) of the application.
"""

import os
import sys
BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from lib.plugin_manager import PluginManager
from lib.exceptions import NoSubscriptionRegex, NoDataRegex, RegexGroupsMissing


PREREGEX = r'\s\d{2}\s\d{2}(:\d{2}){2}\s(?P<hostname>[^\/\s]*)'


def main():
    """Entry point of the application."""
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

    # output the statistics to STDOUT
    pluginManager.statistics.represent()


"""We only start with the executation if we are the main."""
if __name__ == '__main__':
    main()
