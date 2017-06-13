"""Pickup mail aggregation plugin."""

import re

from lib.plugins.plugin_base import RegexFlags
from lib.plugins.simple_plugin import SimplePlugin
from lib import constants


class Pickup(SimplePlugin):
    """Pickup mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/pickup\[')

    def _define_data_regex(self):
        self._dataRegex = [
            (re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                            uid=(?P<''' + constants.UID + r'''>[^ ]+)\s
                            from=<(?P<''' + constants.USERNAME + r'''>[^>]+)''', re.X),
             (RegexFlags.PICKUP,))
        ]