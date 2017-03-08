"""Dovecot statistics plugin."""

from ..lib.plugin_base import PluginBase
import re


class Dovecot(PluginBase):
    """Dovecot statistics plugin."""

    def _define_subscription_regex(self):
        self._define_subscription_regex = re.compile(' dovecot\:')

    def _define_data_regex(self):
        self._define_data_regex = re.compile('\/(?P<hostname>[^\s]*) dovecot: (?P<login>(imap|pop3)-login)')
