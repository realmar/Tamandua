"""Delivery mail aggregation plugin."""

import re

from lib.simple_plugin import SimplePlugin
from lib import constants


class Delivery(SimplePlugin):
    """Delivery mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/(smtp|local)\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           to=<(?P<recipient>[^>]*)>,\s
                           relay=(?P<deliveryrelay>[^,]*).+?
                           status=(?P<deliverystatus>[^\s]*)\s\(
                           (?P<deliverymessage>[^\)]*)''', re.X)
        ]