"""Qmgr mail aggregation plugin."""

import re

from lib.simple_plugin import SimplePlugin
from lib import constants


class Qmgr(SimplePlugin):
    """Qmgr mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/qmgr\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                            from=<(?P<sender>[^>]*)>,\s
                            size=(?P<size>[^,]*)''', re.X)
        ]