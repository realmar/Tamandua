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
            (re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                            client=(?P<connectclient>[^\[]+?)\[
                            (?P<connectip>[^\]]+?)\],\s
                            sasl_method=(?P<saslmethod>[^,]*),\s
                            sasl_username=(?P<saslusername>[^$]*)''', re.X), (RegexFlags.STORETIME,)),

            # no saslauth

            (re.compile(r':\s(?P<' + constants.HOSTNAME_QID + r'>[^:]*):\sclient=(?P<connectclient>[^\]]+?)\[(?P<connectip>[^\]]+?)\]'), (RegexFlags.STORETIME,)),

            # reject RCPT and VRFY
            (re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           (?P<action>reject):\s
                           (?P<rejectstage>[^\s]*)\sfrom\s
                           (?P<connectclient>[^\[]*)\[(?P<connectip>[^\]]*)\]:\s
                           (?P<statuscode>[^\s]*)[^\:]*\:\s
                           (?P<rejectreason>[^\;]*)\;\s
                           (from=<(?P<sender>[^>]*)>\s)?        # VRFY has no from field
                           to=<(?P<recipient>[^>]*)''', re.X), (RegexFlags.STORETIME,)),

            # reject MAIL
            (re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>NOQUEUE):\s
                       (?P<action>reject):\s
                       (?P<rejectstage>[^\s]*)\sfrom\s
                       (?P<connectclient>[^\[]*)\[(?P<connectip>[^\]]*)\]:\s
                       (?P<statuscode>[^\s]*)\s[^\s]*\s
                       (?P<rejectreason>[^;]*)''', re.X), (RegexFlags.STORETIME,)),

            # hold
            re.compile(r''':\s(?P<''' + constants.HOSTNAME_QID + r'''>[^:]*):\s
                           (?P<action>hold).+?>:\s
                           (?P<holdreason>[^;]*);\s
                           from=<(?P<sender>[^>]*)''', re.X)
        ]