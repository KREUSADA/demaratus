import contextlib
import logging

import yaml
from yaml.parser import (
    ParserError as YAMLParserError,
    ScannerError as YAMLScannerError,
    MarkedYAMLError as YAMLMarkedError
)
from .exceptions import (
    ParserInvalidItemError, 
    ParserInvalidTypeError,
    ParserURLError,
    ParserHexError,
    ParserError,
)
from .functions import reformat_dict
from .regex import url_regex, image_regex, hex_code_regex


log = logging.getLogger("red.kreusada.embedbuilder.parser")

def yaml_validator(data):
    try:
        loader = yaml.full_load(data)
    except (YAMLParserError, YAMLScannerError, YAMLMarkedError):
        return False
    if not isinstance(loader, dict):
        return False
    return loader


class Parser(object):
    """
    Builds the embed image for the provided and relevant data.
    The YAML will have been validated before it reaches this point.
    Irrelvant keys are ignored as we are only getting the keys we need
    through dict.get()
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs.get("data")

        self.author = self.data.get("author")
        if self.author and isinstance(self.author, list):
            self.author = reformat_dict(self.author)
            self.author_name = self.author.get("name")
            self.author_url = self.author.get("url")
            self.author_icon_url = self.author.get("icon_url")

        self.footer = self.data.get("footer")
        if self.footer and isinstance(self.footer, list):
            self.footer = reformat_dict(self.footer)
            self.footer_text = self.footer.get("text")
            self.footer_icon_url = self.footer.get("icon_url")

        self.colour = self.data.get("colour") or self.data.get("color")
        self.description = self.data.get("description")
        self.timestamp = self.data.get("timestamp")
        self.title = self.data.get("title")
        self.url = self.data.get("url")

        self.image = self.data.get("image")
        self.thumbnail = self.data.get("thumbnail")

        self.outside_text = self.data.get("outside_text")

        self.fields = self.data.get("fields")

    def __repr__(self) -> str:
        return f"<class {self.__class__.__name__}(data={self.data})>"

    @property
    def __str__(self):
        return self.__repr__

    def __len__(self) -> int:
        return len(self.data.keys())

    async def validparser(self):
        if self.author:
            if not isinstance(self.author, dict):
                raise ParserInvalidTypeError(
                    field="author",
                    invalid_type=type(self.author),
                    supported_types=(dict,)
                )
            if self.author_name:
                if not isinstance(self.author_name, str):
                    raise ParserInvalidTypeError(
                        field="author name",
                        invalid_type=type(self.author_name),
                        supported_types=(str,)
                    )
            if self.author_url:
                if not isinstance(self.author_url, str):
                    raise ParserInvalidTypeError(
                        field="author url",
                        invalid_type=type(self.author_url),
                        supported_types=(str,)
                    )
                if not url_regex.search(self.author_url):
                    raise ParserURLError("author url")
            if self.author_icon_url:
                if not isinstance(self.author_icon_url, str):
                    raise ParserInvalidTypeError(
                        field="author icon_url",
                        invalid_type=type(self.author_icon_url),
                        supported_types=(str,)
                    )
                if not image_regex.search(self.author_icon_url):
                    raise ParserURLError("author icon_url")
        if self.footer:
            if not isinstance(self.footer, dict):
                raise ParserInvalidTypeError(
                    field="footer",
                    invalid_type=type(self.footer),
                    supported_types=(dict,)
                )
            if self.footer_text:
                if not isinstance(self.footer_text, str):
                    raise ParserInvalidTypeError(
                        field="footer text",
                        invalid_type=type(self.footer_text),
                        supported_types=(str,)
                    )
            if self.footer_icon_url:
                if not isinstance(self.footer_icon_url, str):
                    raise ParserInvalidTypeError(
                        field="footer icon_url",
                        invalid_type=type(self.footer_icon_url),
                        supported_types=(str,)
                    )
        if self.colour:
            if not isinstance(self.colour, str):
                raise ParserInvalidTypeError(
                    field="colour",
                    invalid_type=type(self.colour),
                    supported_types=(str,)
                )
            if not hex_code_regex.match(self.colour):
                if not self.colour == "DEFAULT":
                    raise ParserHexError(self.colour)
        if self.description:
            if not isinstance(self.description, str):
                raise ParserInvalidTypeError(
                    field="description",
                    invalid_type=type(self.description),
                    supported_types=(str,)
                )
        if self.timestamp:
            if not isinstance(self.timestamp, bool):
                raise ParserInvalidTypeError(
                    field="timestamp",
                    invalid_type=type(self.timestamp),
                    supported_types=(bool,)
                )
        if self.title:
            if not isinstance(self.title, str):
                raise ParserInvalidTypeError(
                    field="title",
                    invalid_type=type(self.title),
                    supported_types=(str,)
                )
        if self.url:
            if not isinstance(self.url, str):
                raise ParserInvalidTypeError(
                    field="url",
                    invalid_type=type(self.url),
                    supported_types=(str,)
                )
            if not url_regex.search(self.url):
                raise ParserURLError("url")
        if self.image:
            if not isinstance(self.image, str):
                raise ParserInvalidTypeError(
                    field="image",
                    invalid_type=type(self.image),
                    supported_types=(str,)
                )
            if not image_regex.search(self.image):
                raise ParserURLError("image")
        if self.thumbnail:
            if not isinstance(self.thumbnail, str):
                raise ParserInvalidTypeError(
                    field="thumbnail",
                    invalid_type=type(self.thumbnail),
                    supported_types=(str,)
                )
            if not image_regex.search(self.thumbnail):
                raise ParserURLError("thumbnail")
        if self.outside_text:
            if not isinstance(self.outside_text, str):
                raise ParserInvalidTypeError(
                    field="outside_text",
                    invalid_type=type(self.outside_text),
                    supported_types=(str,)
                )
        if self.fields:
            if not isinstance(self.fields, list):
                raise ParserInvalidTypeError(
                    field="fields",
                    invalid_type=type(self.fields),
                    supported_types=(list,)
                )
            fields = reformat_dict(self.fields)
            log.debug(fields)
            for key, value in fields.items():
                if len(value) == 1 or len(value) == 2:
                    if not isinstance(value[0], str):
                        raise ParserError(
                            f"The '{key}' field value parameter must be a str"
                        )
                if len(value) == 2:
                    if not isinstance(value[1], bool):
                        raise ParserError(
                            f"The '{key}' field inline parameter must be a bool"
                        )