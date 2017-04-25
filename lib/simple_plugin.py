from .plugin_base import PluginBase


class SimplePlugin(PluginBase):
    def _format_hostname(self, hostname: str) -> str:
        return hostname.replace('-', '')

    def __specify_regex_group_name(self, dataRegexMatches, preRegexMatches):
        newDataRegexMatches = {}

        hostname = self._format_hostname(preRegexMatches.get('hostname'))
        for key, value in dataRegexMatches.items():
            newKey = key.replace('hostname', hostname)
            newDataRegexMatches[newKey] = value

        return newDataRegexMatches

