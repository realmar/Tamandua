"""Spamd mail aggregation plugin."""

import re

from lib.simple_plugin import SimplePlugin
from lib import constants


class Spamd(SimplePlugin):
    """Spamd mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' spamd\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'''result:\s.\s(?P<spamscore>[^\s]*)\s-\s
                           (?P<spamdesc>[^\s]*)\s
                           scantime=(?P<spamscantime>[^,]*),
                           size=(?P<size>[^,]*),
                           user=(?P<spamuser>[^,]*),
                           uid=(?P<spamuid>[^,]*),
                           required_score=(?P<spamrequiredscore>[^,]*).+?<
                           (?P<''' + constants.MESSAGEID + r'''>[^>]*)''', re.X)
        ]