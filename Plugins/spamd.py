"""Spamd statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Spamd(PluginBase):
    """Spamd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' spamd\[')

    def _define_data_regex(self):
        self._dataRegex = re.compile('\/(?P<hostname>[^\s]*) spamd\[[^\]]*\]: spamd: (?P<servicename>[^\ ]* [^\ ]*) \(\d')
