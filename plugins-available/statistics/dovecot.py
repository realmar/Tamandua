"""Dovecot statistics plugin."""

from lib.plugins.plugin_base import PluginBase
import re


class Dovecot(PluginBase):
    """Dovecot statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' dovecot\:')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'(?P<servicename_login>(imap|pop3)-login)')  # ,
            # re.compile(r'imap\((?P<servicename_user>[^\)]*)')
        ]
