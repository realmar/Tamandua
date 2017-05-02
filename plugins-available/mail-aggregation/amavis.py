"""Amavis mail aggregation plugin."""

import re

from lib.plugins.simple_plugin import SimplePlugin
from lib import constants


class Amavis(SimplePlugin):
    """Amavis mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' amavis\[')

    def _define_data_regex(self):
        self._dataRegex = [
            # Passed CLEAN

            re.compile(r'''\)\s(?P<virusresult>[^\{]*){
                           (?P<virusaction>[^\}]*).+?\]\s<
                           (?P<sender>[^>]*)>\s->\s<
                           (?P<recipient>[^>]*)>.+?Queue-ID:\s
                           (?P<''' + constants.PHD_MXIN_QID + r'''>[^,]*),\sMessage-ID:\s<
                           (?P<''' + constants.MESSAGEID + r'''>[^>]*)?(.+?queued_as:\s
                           (?P<''' + constants.PHD_IMAP_QID + r'''>[^,]*))''', re.X),

            # NOT Passed

            re.compile(r'''\)\s(?P<virusresult>[^\{]*){
                           (?P<virusaction>[^\}]*).+?\]\s<
                           (?P<sender>[^>]*)>\s->\s<
                           (?P<recipient>[^>]*)>.+?Queue-ID:\s
                           (?P<''' + constants.PHD_MXIN_QID + r'''>[^,]*),\sMessage-ID:\s<
                           (?P<''' + constants.MESSAGEID + r'''>[^>]*)''', re.X),

            # Truncated line (eg. when the lines contains a huge amount of recipients)

            re.compile(r'''Queue-ID:\s(?P<''' + constants.PHD_MXIN_QID + r'''>[^,]*),\s
                           Message-ID:\s<(?P<''' + constants.MESSAGEID + r'''>[^>]*)?(.+?
                           queued_as:\s(?P<''' + constants.PHD_IMAP_QID + r'''>[^,]*))''', re.X)
        ]