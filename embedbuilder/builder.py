import contextlib
import datetime
import discord

from .converters import colour_converter
from .functions import reformat_dict

now = datetime.datetime.now()

class Builder(object):
    """
    The central embed builder used to build the embeds
    with the parsed and cleaned data.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs.get("data")

        self.author = self.data.get("author")
        if self.author:
            self.author = reformat_dict(self.author)
            self.author_name = self.author.get("name")
            self.author_url = self.author.get("url")
            self.author_icon_url = self.author.get("icon_url")

        self.footer = self.data.get("footer")
        if self.footer:
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
        return f"<class {self.__class__.__name__}(data={self.data}>"

    @property
    def __str__(self) -> str:
        return self.__repr__

    def __len__(self) -> int:
        return len(set(self.data.keys()))

    async def builder(self, ctx):
        kwargs = {}
        if self.title:
            kwargs["title"] = self.title
        if self.description:
            kwargs["description"] = self.description
        if self.url:
            kwargs["url"] = self.url
        if self.timestamp:
            kwargs["timestamp"] = now
        if self.colour:
            if self.colour == "DEFAULT":
                self.colour = await ctx.embed_colour()
            kwargs["colour"] = colour_converter(self.colour)
        embed = discord.Embed(**kwargs)
        if self.author:
            kwargs = {}
            if self.author_name:
                kwargs["name"] = self.author_name
            if self.author_url:
                kwargs["url"] = self.author_url
            if self.author_icon_url:
                kwargs["icon_url"] = self.author_icon_url
            embed.set_author(**kwargs)
        if self.footer:
            kwargs = {}
            if self.footer_text:
                kwargs["text"] = self.footer_text
            if self.footer_icon_url:
                kwargs["icon_url"] = self.footer_icon_url
            embed.set_footer(**kwargs)
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.fields:
            fields = reformat_dict(self.fields)
            for field in list(fields.keys())[:16]:
                kwargs = {
                    "name": field,
                    "value": fields.get(field)[0],
                }
                with contextlib.suppress(IndexError):
                    kwargs["inline"] = fields.get(field)[1]
                embed.add_field(**kwargs)
            
        return (embed, self.outside_text)
