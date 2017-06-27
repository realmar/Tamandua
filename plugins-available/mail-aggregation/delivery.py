"""Delivery mail aggregation plugin."""

import re

from src import constants
from src.plugins.bases.simple_plugin import SimplePlugin


class Delivery(SimplePlugin):
    """Delivery mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/(smtp|local|pipe)\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           to=<(?P<recipient>[^>]*)>,\s
                           (orig_to=<(?P<orig_recipient>[^>]*)>,\s)?
                           relay=(?P<deliveryrelay>[^,]*).+?
                           status=(?P<deliverystatus>[^\s]*)\s\(
                           (?P<deliverymessage>[^\)]*)''', re.X)
        ]
