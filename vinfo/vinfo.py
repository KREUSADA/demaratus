"""
MIT License

Copyright (c) 2021 Kreusada

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pip
import sys
import redbot
import discord
import logging
import lavalink
import distutils.sysconfig

from redbot.core import commands
from redbot.core.utils.chat_formatting import box, bold

log = logging.getLogger("red.kreusada.vinfo")

base = "{}: {}\n{}: {}.{}.{}\n{}: {}\n\n{}: {}\n{}: {}"

RETURN_TYPE_1 = box(
    "- Could not find a version for `{}`.",
    lang="diff"
)
RETURN_TYPE_2 = box(
    "- You do not have an installed module named `{}`.", 
    lang="diff"
)
RETURN_TYPE_3 = box(
    "Builtin Red cogs do not have version attributes by default. Perhaps you're looking for your Red version, which would be {}.",
    lang="yaml"
)

REDBOT_CORE_COGS = [
    "Admin",
    "Alias",
    "Audio",
    "Bank",
    "Cleanup",
    "CustomCom",
    "Downloader",
    "Economy",
    "Filter",
    "General",
    "Image",
    "Mod",
    "ModLog",
    "Mutes",
    "Permissions",
    "Reports",
    "Streams",
    "Trivia",
    "Warnings",
]


class Vinfo(commands.Cog):
    """
    Get versions of 3rd party cogs, and modules.
    """

    __author__ = [
        "Kreusada",
    ]
    __version__ = "1.0.1"

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def modvinfo_format(mods):
        formatter = (
            bold("Red"),
            redbot.version_info,
            bold("Python (Sys)"),
            *sys.version_info[:3],
            bold("discord.py"),
            discord.__version__,
            bold("PIP"),
            pip.__version__,
            bold("Lavalink"),
            lavalink.__version__,
        )
        description = mods.format(*formatter)
        return discord.Embed(
            title="Common Modules",
            description=description,
        )

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    # Commands

    @commands.is_owner()
    @commands.group(aliases=["versioninfo"])
    async def vinfo(self, ctx):
        """Get versions of 3rd party cogs, and modules."""

    @vinfo.command()
    async def cog(self, ctx, cog: str):
        """
        Get the version information for a Red cog.

        The cog must be loaded, and provided in the correct casing.
        """
        await ctx.trigger_typing()
        
        if cog not in self.bot.cogs:
            return await ctx.send(box(f"- Could not find a cog matching `{cog}`.", lang='diff'))

        Cog = self.bot.get_cog(cog)

        # Note that cogs won't have a `version_info` attr unlike some modules, so
        # we'll skip finding that attr because it will return False 99% of the time.

        if hasattr(Cog, "__version__"):
            return await ctx.send(box(f"{cog} version: {getattr(Cog, '__version__')}", lang='yaml'))
        elif cog in REDBOT_CORE_COGS:
            return await ctx.send(RETURN_TYPE_3.format(redbot.version_info))
        else:
            await ctx.send(box(f"- Could not find a version for {cog}.", lang='diff'))

    @vinfo.command(aliases=["module", "dep", "dependency"], usage="<module or dependency>")
    @commands.bot_has_permissions(embed_links=True)
    async def mod(self, ctx, module: str = None):
        """Get module versions."""
        
        if not module:
            embed = self.modvinfo_format(base)
            embed.color = await ctx.embed_colour()
            embed.set_footer(
                text="Find a specific module version by adding the module argument."
            )
            await ctx.send(embed=embed)
            return await ctx.send_help()

        # If `version_info` is defined, we should refer to this first.
        version_info = "version_info"
        versionattr = "__version__"
        shortversionattr = '_version_'
        version = 'version'

        pypath = str(distutils.sysconfig.get_python_lib(standard_lib=True))
        await ctx.trigger_typing()

        try:
            MOD = __import__(module)
        except ModuleNotFoundError as mnfe:
            return await ctx.send(RETURN_TYPE_2.format(module))


        if hasattr(MOD, version_info):
            vinfo = [getattr(MOD, version_info), "." + version_info]

        elif hasattr(MOD, versionattr):
            vinfo = [getattr(MOD, versionattr), "." + versionattr]

        elif hasattr(MOD, shortversionattr):
            vinfo = [getattr(MOD, shortversionattr), "." + shortversionattr]

        elif hasattr(MOD, version):
            vinfo = [getattr(MOD, version), "." + version]

        elif MOD.__file__.lower().startswith(pypath.lower()):
            vinfo = [(sys.version_info[:3]), "[Core/Builtin Python]"]

        else:
            log.info(f"[From {ctx.channel.id}] {module} path: {MOD.__file__}")
            return await ctx.send(
                RETURN_TYPE_1.format(MOD.__name__)
            )

        
        if isinstance(vinfo[0], tuple) and vinfo[1].endswith("[Core/Builtin Python]"):
            value = ("{}." * len(vinfo[0])).strip('.').format(*vinfo[0])
            attr = f"None {vinfo[1]}"
        
        elif isinstance(vinfo[0], tuple):
            value = ("{}." * len(vinfo[0])).strip('.').format(*vinfo[0])
            attr = f"`{MOD.__name__}{vinfo[1]}`"

        elif isinstance(vinfo[0], list):
            value = ("{}." * len(vinfo[0])).strip('.').format(*vinfo[0])
            attr = f"`{MOD.__name__}{vinfo[1]}`"

        else:
            value = vinfo[0]
            attr = f"`{MOD.__name__}{vinfo[1]}`"


        await ctx.send(
            box(
                f"Attribute: {attr}\nFound version info for [{module}]: {value}",
                lang="yaml",
            )
        )
