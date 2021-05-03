import asyncio

import discord
import yaml
from redbot.core import commands

from .builder import Builder
from .exceptions import ParserExceptions
from .functions import (
    asset,
    cleanup_code,
    format_traceback
)
from .mixins import MixinMeta
from .parser import Parser, yaml_validator


class Commands(MixinMeta):
    """
    Seperate file for all the interactable commands
    within the cog.

    The functions also trigger the parser and builder
    classes.

    Settings and config is found in settings.py
    """

    @commands.group()
    async def embed(self, ctx):
        """Create, manage, and store embeds."""

    @embed.command(name="create")
    async def embed_create(self, ctx):
        """Create an embed using YAML."""
        check = lambda x: x.author == ctx.author and x.channel == ctx.channel
        await ctx.send(
            "Now you need to compose your YAML. For reference, see below: "
            + asset
        )
        try:
            content = await self.bot.wait_for("message", timeout=250, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond.")
        content = content.content
        valid = yaml_validator(cleanup_code(content))
        if not valid:
            return await ctx.send("Please provide valid YAML.")
        try:
            parser = Parser(data=valid)
            await parser.validparser()
        except ParserExceptions as e:
            return await ctx.send(format_traceback(e))
        build = Builder(data=valid)
        build = await build.builder(ctx)
        await ctx.send(embed=build[0], content=build[1])
