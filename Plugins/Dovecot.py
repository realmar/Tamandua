"""Dovecot statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Dovecot(PluginBase):
    """Dovecot statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' dovecot\:')

    def _define_data_regex(self):
        self._dataRegex = re.compile('\/(?P<hostname>[^\s]*) dovecot: (?P<servicename_login>(imap|pop3)-login)')
