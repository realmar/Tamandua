"""Lda mail aggregation plugin. (Sieve)"""

import re

from src import constants
from src.plugins.bases.simple_plugin import SimplePlugin


class Lda(SimplePlugin):
    """Lda mail aggregation plugin for sieve messages."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile('\sdovecot: lda\(')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'sieve:\smsgid=<(?P<' + constants.MESSAGEID + r'>[^>]+)>:\s(?P<sievemessage>[^\n]+)', re.X)
        ]
