import asyncio
import datetime
import json
import logging
import pathlib
import sys
from typing import Literal, Union

import discord
import yaml
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import (
    italics, 
    humanize_list, 
    inline, 
    box
)
from yaml.parser import (
    MarkedYAMLError, 
    ParserError, 
    ScannerError
)

with open(pathlib.Path(__file__).parent / "data" / "publish.yaml") as f:
    example_cog_creation_yaml = box("".join(f.readlines()), lang="yaml")

with open(pathlib.Path(__file__).parent / "data" / "remove.yaml") as f:
    example_cog_removal_yaml = box("".join(f.readlines()), lang="yaml")

def shorten_data(data, cut):
    cut = cut - 3
    return data[:cut] + '...'

def shorten_list(data, cut):
    slicer = data[:cut]
    left = len(data[cut:])
    return ", ".join(slicer) + f" and {left} more..."

def get_plural_author(field: Union[list, str]):
    author = "Author"
    if isinstance(field, list) and len(field) > 1:
        author += "s"
    return author    

def format_authors(content: Union[list, str]):
    if isinstance(content, list):
        if len(content) > 5:
            return shorten_list(content, 3)
        return ", ".join(content)
    return content

log = logging.getLogger("red.kreusada.cogfeed")


class ParserInvalidTypeError(Exception):
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

class ParserInvalidItemError(Exception):
    """
    Raised when an item in a list does not follow the rejeme.
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

class ParserRequiredKeyError(Exception):
    """
    Raised when a required key does not exist in the data.
    """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"The \"{self.key}\" key is required"

class ParserGhostURLError(Exception):
    """
    Raised when a field has been opted into which requires the `github_url` key.
    """
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"You must provide a `github_url` key if you wish to opt into adding the {self.key}"


PublishType = Literal["creation", "removal"]


class EmbedBuilder(object):
    """
    Builds the embed image for the provided and relevant data.
    The YAML will have been validated before it reaches this point.
    Irrelvant keys are ignored as we are only getting the keys we need
    through dict.get()
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs.get("data")
        self.name = self.data.get("name")
        self.author = self.data.get("author")
        self.description = self.data.get("description")
        self.requirements = self.data.get("requirements")
        self.tags = self.data.get("tags")
        self.end_user_data_statement = self.data.get("end_user_data_statement")
        self.install_guide = self.data.get("install_guide", False)
        self.github_url = self.data.get("github_url")
        self.title_link = self.data.get("title_link")
        # list of all viable keys
        self.key_list = [
            "name", 
            "author",
            "description",
            "requirements",
            "tags",
            "end_user_data_statement",
            "install_guide",
            "github_url",
            "smart_link_title",
        ]
        # Removal build
        self.reason = self.data.get("reason")
        self.additional_info = self.data.get("additional_info")
        # Misc
        self.publish_type = kwargs.get("publish_type")

    def __repr__(self) -> str:
        return f"<class {self.__class__.__name__}(data={self.data})>"

    @property
    def __str__(self):
        return self.__repr__

    def __len__(self) -> int:
        return len(self.data.keys())

    def format_build(self, ctx):
        if not self.name:
            raise ParserRequiredKeyError("name")
        if not isinstance(self.name, str):
            raise ParserInvalidTypeError(
                field="name",
                invalid_type=type(self.name),
                supported_types=(str,)
            )

        if self.author:
            if not isinstance(self.author, (str, list)):
                raise ParserInvalidTypeError(
                    field="author",
                    invalid_type=type(self.author),
                    supported_types=(str, list)
                )
            if isinstance(self.author, list):
                for author in self.author:
                    if not isinstance(author, str):
                        raise ParserInvalidItemError(
                            item=author,
                            array="author",
                            literal_array=self.author
                        )
        else:
            self.author = ctx.author.name

        if self.publish_type == "removal":
            if self.reason:
                if not isinstance(self.reason, str):
                    raise ParserInvalidTypeError(
                        field="reason",
                        invalid_type=type(self.reason),
                        supported_types=(str,)
                    )

            if self.additional_info:
                if not isinstance(self.additional_info, str):
                    raise ParserInvalidTypeError(
                        field="additional_info",
                        invalid_type=type(self.additional_info),
                        supported_types=(str,)
                    )
        else:
            if self.description:
                if not isinstance(self.description, str):
                    raise ParserInvalidTypeError(
                        field="description",
                        invalid_type=type(self.description),
                        supported_types=(str,)
                    )
            else:
                self.description = "No description was provided."

            if self.requirements:
                if not isinstance(self.requirements, list):
                    raise ParserInvalidTypeError(
                        field="requirements",
                        invalid_type=type(self.requirements),
                        supported_types=(list,)
                    )
                if isinstance(self.requirements, list):
                    for requirement in self.requirements:
                        if not isinstance(requirement, str):
                            raise ParserInvalidItemError(
                                item=requirement,
                                array="requirements",
                                literal_array=self.requirements
                            )

            if self.tags:
                if not isinstance(self.tags, list):
                    raise ParserInvalidTypeError(
                        field="tags",
                        invalid_type=type(self.tags),
                        supported_types=(list,)
                    )
                if isinstance(self.tags, list):
                    for tag in self.tags:
                        if not isinstance(tag, str):
                            raise ParserInvalidItemError(
                                item=tag,
                                array="tags",
                                literal_array=self.tags
                            )

            if not self.end_user_data_statement:
                raise ParserRequiredKeyError("end_user_data_statement")
            if not isinstance(self.end_user_data_statement, str):
                raise ParserInvalidTypeError(
                    field="end_user_data_statement",
                    invalid_type=type(self.end_user_data_statement),
                    supported_types=(str,)
                )

            if self.install_guide:
                if not isinstance(self.install_guide, bool):
                    raise ParserInvalidTypeError(
                        field="install_guide",
                        invalid_type=type(self.install_guide),
                        supported_types=(bool,)
                    )

            if self.install_guide:
                if not isinstance(self.install_guide, bool):
                    raise ParserInvalidTypeError(
                        field="install_guide",
                        invalid_type=type(self.install_guide),
                        supported_types=(bool,)
                    )
                if not self.github_url:
                    raise ParserGhostURLError("install guide")

            if self.github_url:
                if not isinstance(self.github_url, str):
                    raise ParserInvalidTypeError(
                        field="github_url",
                        invalid_type=type(self.github_url),
                        supported_types=(str,)
                    )

            if self.title_link:
                if not isinstance(self.title_link, str):
                    raise ParserInvalidTypeError(
                        field="title_link",
                        invalid_type=type(self.title_link),
                        supported_types=(str,)
                    )
            

        plural_author = get_plural_author(self.author)
        author_content = format_authors(self.author)
        if isinstance(self.author, str):
            primary_author = self.author
        else:
            primary_author = format_authors(self.author[0])

        if self.publish_type == "creation":
            install_description = (
                f"- `[p]repo add {primary_author} {self.github_url}`\n"
                f"- `[p]cog install {primary_author} {self.name.lower()}`"
            )

            kwargs = {
                "title": self.name,
                "description": self.description,
                "timestamp": datetime.datetime.now(),
                "color": 0x6ac6af
            }
            if self.title_link:
                kwargs["url"] = self.title_link
                
            embed = discord.Embed(**kwargs)

            if isinstance(self.author, list):
                self.author = ", ".join(self.author)

            embed.add_field(name=plural_author, value=self.author, inline=True)
            if self.requirements:
                embed.add_field(name="Requirements", value=", ".join(self.requirements), inline=True)
            if self.end_user_data_statement:
                embed.add_field(name="End User Data Statement", value=self.end_user_data_statement, inline=False)
            if self.install_guide:
                embed.add_field(name="Installation Instructions", value=install_description, inline=False)
            if self.tags:
                embed.set_footer(text="Tags: " + ", ".join(self.tags[:7]))

            embed.set_author(name="Added cog", icon_url=ctx.author.avatar_url)
        else:
            kwargs = {
                "title": self.name,
                "description": self.reason,
                "color": 0xe84e4e,
            }

            embed = discord.Embed(**kwargs)
            embed.add_field(
                name=plural_author,
                value=author_content,
                inline=True
            )

            if self.additional_info:
                embed.add_field(
                    name="Additional Information",
                    value=self.additional_info,
                    inline=False
                )
            embed.set_author(name="Removed cog", icon_url=ctx.author.avatar_url)

        return embed


    def __eq__(self, o) -> bool:
        return isinstance(o, self.__class__) and o.id == self.id

    def __ne__(self, o) -> bool:
        return not self.__eq__(o)
            

class CogFeeds(commands.Cog):
    """Publish your cogs to a new channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 953478905834590284, force_registration=True)
        self.config.register_guild(
            publish_feed=None,
            remove_feed=None,
        )

    @staticmethod
    def has_cli_flag(flag):
        return f"--{flag}" in sys.argv

    @staticmethod
    def cleanup_code(content):
        # From redbot.core.dev_commands, thanks will :P
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip("` \n")

    @staticmethod
    def format_traceback(exc, lang):
        e = "An exception occured whilst parsing your data."
        boxit = lambda x, y: box(f"{e}\n\t{x}: {y}", lang=lang)
        return boxit(exc.__class__.__name__, exc)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        _channel = await self.config.guild(channel.guild).channel()
        if channel.id == _channel:
            await self.config.guild(channel.guild).channel.clear()

    async def yaml_parser(self, ctx, content, publish_type: PublishType):
        # Passing ctx for self.prepare_builder
        content = self.cleanup_code(content)
        failure_message = "Please provide valid YAML."
        try:
            loader = yaml.full_load(content)
        except (ParserError, MarkedYAMLError, ScannerError):
            return await ctx.send(failure_message)
        if not isinstance(loader, dict):
            return await ctx.send(failure_message)
        await self.prepare_builder(ctx, loader, publish_type)

    async def prepare_builder(self, ctx, content, publish_type: PublishType):
        try:
            builder = EmbedBuilder(
                data=content,
                publish_type=publish_type
            )
            builder = builder.format_build(ctx)
        except (
            ParserRequiredKeyError, 
            ParserInvalidTypeError, 
            ParserInvalidItemError,
            ParserGhostURLError
        ) as e:
            return await ctx.send(self.format_traceback(e, "yaml"))
        settings = await self.config.guild(ctx.guild).all()
        if publish_type == "creation":
            channel = settings["publish_feed"]
            conf = "Cog publishing was successful."
        else:
            channel = settings["remove_feed"]
            conf = "Cog removal was successful."
        channel = self.bot.get_channel(channel)
        if not channel:
            await ctx.send("Looks like the cogfeed channel doesn't exist anymore.")
            return
        if not channel.permissions_for(ctx.me).send_messages:
            await ctx.send("I don't have permissions to send messages to the cogfeed channel.")
            return
        if not channel.permissions_for(ctx.me).embed_links or not await ctx.embed_requested():
            await ctx.send("I don't have permissions to send embeds to the cogfeed channel.")
            return
        try:
            await channel.send(embed=builder)
        except discord.HTTPException as e:
            return await ctx.send(self.format_traceback(e, "py"))
        await ctx.send(conf)

    @commands.group()
    async def cogfeed(self, ctx):
        """Publish and unpublish cogs, and edit their settings."""
        pass

    @cogfeed.command(name="publish")
    async def cogfeed_publish(self, ctx):
        """Announce/publish your new cog to the feed channel."""
        check = lambda x: x.author == ctx.author and x.channel == ctx.channel
        await ctx.send(
            "Now you need to compose your YAML. For reference, see below: "
            + example_cog_creation_yaml
        )
        try:
            content = await self.bot.wait_for("message", timeout=250, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond.")
        content = content.content
        async with ctx.typing():
            await self.yaml_parser(ctx, content, "creation")

    @cogfeed.command(name="remove")
    async def cogfeed_remove(self, ctx):
        """Announce the removal of a cog."""
        check = lambda x: x.author == ctx.author and x.channel == ctx.channel
        await ctx.send(
            "Now you need to compose your YAML. For reference, see below: "
            + example_cog_removal_yaml
        )
        try:
            content = await self.bot.wait_for("message", timeout=250, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond.")
        content = content.content
        async with ctx.typing():
            await self.yaml_parser(ctx, content, "removal")

    @cogfeed.group(name="set")
    async def cogfeed_set(self, ctx):
        """Settings for cogfeeds."""

    @cogfeed_set.command()
    async def publishchannel(self, ctx, channel: discord.TextChannel):
        """Set the cog publishing channel."""
        await self.config.guild(ctx.guild).publish_feed.set(channel.id)
        await ctx.send(f"Publish channel set to {channel.mention}.")

    @cogfeed_set.command()
    async def removechannel(self, ctx, channel: discord.TextChannel):
        """Set the cog removal channel."""
        await self.config.guild(ctx.guild).remove_feed.set(channel.id)
        await ctx.send(f"Removal channel set to {channel.mention}.")

def setup(bot):
    bot.add_cog(CogFeeds(bot))

with open(pathlib.Path(__file__).parent / "info.json") as fp:
    data_statement = json.load(fp)["end_user_data_statement"]