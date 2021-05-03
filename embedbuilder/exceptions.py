from redbot.core.utils.chat_formatting import humanize_list

class ParserExceptions(Exception):
    """
    Base exception for all Parser related errors.

    This class will be inherited from when catching exceptions.
    """
    pass

class ParserInvalidTypeError(ParserExceptions):
    """
    Raised when an unsupported type is provided to the parser.
    """

    def __init__(self, **kwargs):
        self.field_name = kwargs.get("field")
        self.invalid_type = kwargs.get("invalid_type")
        self.supported_types = kwargs.get("supported_types")

    def __str__(self):
        humanized = humanize_list(items=[x.__name__ for x in self.supported_types], style='or')
        return (
            f"The type of the '{self.field_name}' field must be "
            f"{humanized}, not {self.invalid_type.__name__}"
        )

class ParserInvalidItemError(ParserExceptions):
    """
    Raised when an item in a list does not follow the requirements.
    """

    def __init__(self, **kwargs):
        self.item = kwargs.get("item")
        self.array = kwargs.get("array")
        self.literal_array = kwargs.get("literal_array")

    def __str__(self):
        return (
            f"An item in your \"{self.array}\" list must be a str, not {type(self.item).__name__}. "
            f"(Sequence position {self.literal_array.index(self.item)})"
        )

class ParserURLError(ParserExceptions):
    """
    Raised when a URL is faulty and does not match the specified regex.
    """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return (
            f"The provided URL for the '{self.key}' key was faulty"
        )

class ParserHexError(ParserExceptions):
    """
    Raised when the embed color hex code is invalid.
    """

    def __init__(self, _hex):
        self._hex = _hex

    def __str__(self):
        return (
            f"{self._hex} is not a valid hex code."
        )

class ParserError(ParserExceptions):
    """
    A more general exception without arguments.
    """
    pass