"""Cleanup mail aggregation plugin."""

import re

from src import constants
from src.plugins.bases.simple_plugin import SimplePlugin


class Cleanup(SimplePlugin):
    """Cleanup mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/cleanup\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           message-id=<(?P<''' + constants.MESSAGEID + r'''>[^>]*)''', re.X)
        ]
