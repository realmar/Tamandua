"""Lmtp mail aggregation plugin."""

import re

from lib.plugins.simple_plugin import SimplePlugin
from lib import constants


class Lmtp(SimplePlugin):
    """Lmtp mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/lmtp\[')

    def _define_data_regex(self):
        self._dataRegex = [
            # stats=sent
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                            to=<(?P<recipient>[^>]*)>(,\s
                            orig_to=<(?P<orig_recipient>[^>]*))?.*
                            queued\sas\s
                                (?P<''' + constants.PHD_IMAP_QID + r'''>[^\)]*)''', re.X),

            # status = NOT sent
            re.compile(
                r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                    to=<(?P<recipient>[^>]*).+?
                    status=(?P<lmtpstatus>[^\s]*)\s
                    \((?P<lmtpmsg>[^\)]*)''', re.X)
        ]