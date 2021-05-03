import json
import logging 
import pathlib

from redbot.core import Config, commands

from .mixins import MetaClass
from .settings import Settings
from .commands import Commands

log = logging.getLogger("red.kreusada.embedbuilder")


class EmbedBuilder(Settings, Commands, commands.Cog, metaclass=MetaClass):
    """Build, store, and manipulate with embeds using YAML."""

    __author__ = ["Kreusada"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 0x93824723942, force_registration=True)
        self.config.register_user(
            saved_templates=[]       
        )

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

with open(pathlib.Path(__file__).parent / "info.json") as fp:
    data = json.load(fp)["end_user_data_statement"]

def setup(bot):
    bot.add_cog(EmbedBuilder(bot))