""""""


class Singleton(type):
    """
    Singleton metaclass.

    Assign this class as metaclass to any class which should be a singleton.

    For example:

    class MySingleton(metaclass=Singleton):
        pass

    Access the instance:

    MySingleton().<member>

    Sidenote: if you dont know what this is, read here: https://sourcemaking.com/design_patterns/singleton

    Also note that a singleton is actually considered an "antipattern"
    as it eg. makes testing and threading more difficult. We should
    only use it if absolutely necessary.
    Also: Singleton is the OOP thing of a "global variable"
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance