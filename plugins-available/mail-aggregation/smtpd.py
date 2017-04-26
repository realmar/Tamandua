"""Smtpd mail aggregation plugin."""

import re

from lib.plugins.simple_plugin import SimplePlugin
from lib.plugins.plugin_base import RegexFlags
from lib import constants


class Smtpd(SimplePlugin):
    """Smtpd mail aggregation plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/smtpd')

    def _define_data_regex(self):
        self._dataRegex = [
            # saslauth and saslmethod
            (re.compile(r''':\s
                            (?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s[^,]*,\s
                            sasl_method=(?P<saslmethod>[^,]*),\s
                            sasl_username=(?P<saslusername>[^$]*)''', re.X), (RegexFlags.STORETIME,)),

            # no saslauth

            (re.compile(r':\s(?P<' + constants.HOSTNAME_QID + r'>[^:]*):\sclient'), (RegexFlags.STORETIME,)),

            # hold
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>NOQUEUE):\s
                            (?P<action>reject).+?
                            Recipient\saddress\srejected:\s
                                (?P<rejectreason>[^;]*);\s
                            from=<(?P<sender>[^>]*)>\s
                            to=<(?P<recipient>[^>]*)''', re.X),

            # hold
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           (?P<action>hold).+?>:\s
                           (?P<holdreason>[^;]*);\s
                           from=<(?P<sender>[^>]*)''', re.X)
        ]