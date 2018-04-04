"""Postgrey mail aggregation plugin."""

import re

from src import constants
from src.plugins.bases.simple_plugin import SimplePlugin


class Postgrey(SimplePlugin):
    """
    Postgrey mail aggregation plugin.
    It turns out that some postgrey loglines sometime have a queueid
    attached to them. This plugins parses those lines.
    """

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile('\spostgrey\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]+):\s
                           action=(?P<action>[^,]+),\s
                           reason=(?P<actionreason>[^,]+),\s''', re.X)
        ]
