"""
MIT License

Copyright (c) 2021 kreusada

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

import discord

from redbot.core import commands
from redbot.core.utils.chat_formatting import spoiler

class BubbleWrap(commands.Cog):
    """
    Get some bubblewrap.

    This will not work if you have spoilers turned
    off in your user settings.
    """

    __author__ = ["Kreusada", ]
    __version__ = "1.0.0"
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete"""
        return

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bubble"])
    async def bubblewrap(self, ctx):
        """
        Get some bubblewrap.

        This will not work if you have spoilers turned
        off in your user settings.
        """
        pre_processed = f"{spoiler('pop')}" * 7
        processed = f"{pre_processed}\n" * 7
        if await ctx.embed_requested():
            embed = discord.Embed(
                title="Bubblewrap!",
                description=processed,
                color=await ctx.embed_colour(),
            )
            return await ctx.send(embed=embed)
        await ctx.send(processed)