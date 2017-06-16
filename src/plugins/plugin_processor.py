"""Helper classes of the processor plugins."""

import types
from enum import Enum
from abc import ABCMeta, abstractmethod

from ..interfaces import IProcessorPlugin
from .plugin_helpers import add_tag, has_tag 


class ProcessorAction(Enum):
    """Enum which hints external action which should accur on a object given to a processor."""

    KEEP = 1
    DELETE = 2
    NONE = 3


class ProcessorData():
    """
    Wrapper class for data passed to processors.

    It supports hints which may provoke additional logic in the caller.
    Eg. deleting the object given to the processor. Note that
    this is completely dependant on the implementation of the client (caller).
    Eg. MailContainer supports this behavior.
    """

    def __init__(self, data: dict):
        """Constructor of ProcessorData."""
        self.__data = data
        self.action = ProcessorAction.KEEP

    @property
    def data(self):
        """Get stored data."""
        return self.__data


class BaseVerifyProcessor(IProcessorPlugin, metaclass=ABCMeta):
    """
    Base class of a verify processor.

    This class should provide the user with generic
    functionality for verifying the integrity of some dict.

    It subscribes itself to a dict using the given tags in
    _matchingTags. For dicts with those tags, the processor
    will verify their integrity.

    The subscription process can be overwritten using the
    _custom_match method. (overwrite it)

    Using _requiredFields it is possible to define which fields
    are required to be present in order for a dict to not get
    tagged as 'incomplete'. Those fields may also be required
    to hold a specific value.

    If this processor verifies different dicts, the _requiredFields
    should contain the lowest common fields. Using _get_additional_fields
    you may return a list with additional fields to be verified. (Depending
    on the state of the to be checked dict.)

    Defining _requiredFields:

    self._requiredFields = [
        'sender',                       # check if the field 'sender' is present

        ('uid', 3)                      # check if 'uid' is present and
                                        # it is exactly equal to 3

        ('deliverystatus', 'sent')      # check if the field 'deliverystatus' is present
                                        # and if it is found somewhere in 'sent'

        ('spamscore', lambda x: x > 5)  # check if 'spamscore' is present and
                                        # verify its content using a
                                        # predicate of type Callable[[str], bool]
    ]
    """

    def __init__(self):
        """Constructor of BaseVerifyProcessor."""
        self._matchingTags = None
        self._requiredFields = None

        self._setup()

        # verify user data

        if not isinstance(self._requiredFields, list):
            self._requiredFields = []

        if not isinstance(self._matchingTags, list):
            self._matchingTags = []

    @abstractmethod
    def _setup(self) -> None:
        """
        Setup _matchingTgas and _requiredFields.

        Clients are required to implement this method.
        """
        pass

    def _custom_match(self, obj: ProcessorData) -> bool:
        """
        Overwrite the subscription process.

        If the return value of this method evaluates to True, then
        the processor will verify the integrity of a given dict.

        If you overwrite this method and conditionally want to
        delegate the subscription process to the base class, raise
        NotImplementedError.
        In other words: if this methods raises NotImplementedError,
        the subscription process will be done using the specified tags
        in _matchingTags.
        """
        raise NotImplementedError()

    def _get_additional_fields(self, obj: ProcessorData) -> list:
        """
        Add additional fields to be checked, depending on the object state.

        Return an additional list in the same form as _requiredFields, which
        have to be checked depending on the state of the given dict.
        """
        return []

    def process(self, obj: ProcessorData) -> None:
        """Verify the integrity of a given dict using defined parameters."""
        isResponsible = False

        try:
            isResponsible = self._custom_match(obj)
        except NotImplementedError as e:
            for tag in self._matchingTags:
                if has_tag(obj.data, tag):
                    isResponsible = True

        if isResponsible:
            a = self._requiredFields + self._get_additional_fields(obj)
            for field in self._requiredFields + self._get_additional_fields(obj):
                if isinstance(field, tuple) or isinstance(field, list):
                    isList = True
                else:
                    isList = False

                if isList:
                    f = field[0]
                    content = field[1]
                else:
                    f = field
                    content = None

                if obj.data.get(f) is None:
                    add_tag(obj.data, 'incomplete')
                    return
                else:
                    if content is not None:
                        if isinstance(content, types.LambdaType):
                            if not content(obj.data[f]):
                                add_tag(obj.data, 'incomplete')
                        else:
                            if isinstance(content, str):
                                comp = lambda x, y: x in y
                            else:
                                comp = lambda x, y: x == y

                            if not comp(content, obj.data[f]):
                                add_tag(obj.data, 'incomplete')
                        return

