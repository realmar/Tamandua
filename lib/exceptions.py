"""Custom Exceptions used by the Application."""


class NoSubscriptionRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No subscription regex defined in: " + clsname)


class NoDataRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No data regex defined in: " + clsname)


class RegexGroupsMissing(Exception):
    def __init__(self, clsname, pattern):
        super().__init__("No named regex groups defined in: " + clsname + " pattern: " + pattern)


class MissingConfigField(Exception):
    def __init__(self, field):
        super().__init__("The following field is missing from the config: " + field)


class InvalidConfigField(Exception):
    def __init__(self, field, allowedValues):
        super().__init__("The following field in the config is wrong: " + field + " allowed values are following: " + str(allowedValues))


class MultipleDataSetsUnknown(Exception):
    def __init__(self, clsname):
        super().__init__(clsname + """ has received multiple datasets for
        unknown data. This is either a bug, or you have a custom PluginBase
        class which does something wrong in gather_data. """)


class InvalidRegexFlag(Exception):
    def __init__(self, clsname, pattern):
        super().__init__("Invalid regex-flag in: " + clsname + " pattern: " + pattern)
