"""Module which contains the base plugin for all mail-aggregation plugins."""

from .plugin_base import PluginBase


class SimplePlugin(PluginBase):
    """Simplifies the implementation of PluginBase."""

    @staticmethod
    def _format_hostname(hostname: str) -> str:
        return hostname.replace('-', '')

    def _specify_regex_group_name(self, dataRegexMatches: dict, preRegexMatches: dict) -> dict:
        newDataRegexMatches = {}

        hostname = self._format_hostname(preRegexMatches.get('hostname'))
        for key, value in dataRegexMatches.items():
            newKey = key.replace('hostname', hostname)
            newDataRegexMatches[newKey] = value

        return newDataRegexMatches

