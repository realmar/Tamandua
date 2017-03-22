"""Amavis statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Amavis(PluginBase):
    """Amavis statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' amavis\[')

    def _define_data_regex(self):
        self._dataRegex = [re.compile('\/(?P<hostname>[^\s]*) amavis\[[^\]]*\]: \([^\)]*\) (?P<servicename_virus>[^ ]* [^ ]*)')]
