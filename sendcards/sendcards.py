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
from redbot.core.utils.chat_formatting import bold


class SendCards(commands.Cog):
    """
    Send someone a card!
    """

    __author__ = [
        "Kreusada",
    ]
    __version__ = "1.4.0"

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @commands.group()
    async def send(self, ctx: commands.Context):
        """Send a card to someone!"""

    @send.command()
    async def christmas(
        self,
        ctx: commands.Context,
        user_id: int,
        *,
        message: str,
        image: discord.Attachment = None,
    ):
        """
        Send a christmas card to someone.
        
        Your message will be sent in this format:
        
        Dear [person],
        
        {message}
        
        From [your_name]
        """
        await self.card_send(ctx, "christmas", user_id, message)

    @send.command()
    async def birthday(
        self,
        ctx: commands.Context,
        user_id: int,
        *,
        message: str,
        image: discord.Attachment = None,
    ):
        """
        Send a birthday card to someone.
        
        Your message will be sent in this format:
        
        Dear [person],
        
        {message}
        
        From [your_name]
        """
        await self.card_send(ctx, "birthday", user_id, message)

    @send.command(aliases=["gws"])
    async def getwellsoon(
        self,
        ctx: commands.Context,
        user_id: int,
        *,
        message: str,
        image: discord.Attachment = None,
    ):
        """
        Send a get well soon card to someone.
        
        Your message will be sent in this format:
        
        Dear [person],
        
        {message}
        
        From [your_name]
        """
        await self.card_send(ctx, "get well soon", user_id, message)

    @send.command()
    async def valentine(
        self,
        ctx: commands.Context,
        user_id: int,
        *,
        message: str,
        image: discord.Attachment = None,
    ):
        """
        Send a valentines card to someone.
        
        Your message will be sent in this format:
        
        Dear [person],
        
        {message}
        
        From [your_name]
        """
        await self.card_send(ctx, "valentines", user_id, message)

    async def card_send(
        self, ctx: commands.Context, type: str, user_id: int, message: str
    ):
        if len(message) > 1900:
            return await ctx.send("This message is *too* long. Please try again.")
        if type == "christmas":
            emoji = "\N{CHRISTMAS TREE}"
        elif type == "birthday":
            emoji = "\N{PARTY POPPER}"
        elif type == "get well soon":
            emoji = "\N{THERMOMETER}\N{VARIATION SELECTOR-16}"
        else:
            emoji = "\N{SMILING FACE WITH SMILING EYES AND THREE HEARTS}"
        name = self.bot.get_user(user_id)
        if not name:
            return await ctx.send(f"Could not find a user matching `{user_id}`.")
        title = f"{emoji} {type.title()} card from {ctx.author.name}!"
        description = (
            f"Dear {name.name},\n\n{message}\n\nFrom {ctx.author.name} {emoji}."
        )
        embed = discord.Embed(
            title=title, description=description, color=await ctx.embed_colour()
        )
        embed.set_footer(
            text=f"Send {type} cards by using: {ctx.clean_prefix}send {type.replace(' ', '')}!"
        )
        if ctx.message.attachments:
            image = await ctx.message.attachments[0].to_file()
            embed.set_image(url="attachment://" + str(image.filename))
        try:
            if await ctx.embed_requested():
                await name.send(
                    embed=embed, file=image if ctx.message.attachments else None
                )
            else:
                await ctx.send(f"{bold(title)}\n\n{description}")
            return await ctx.send(
                f"A {type.capitalize()} card has been successfully sent to {name.name}! {emoji}"
            )
        except discord.Forbidden:
            return await ctx.send(
                f"Unfortunately, {name.name} has their DMs turned off. Sorry!"
            )