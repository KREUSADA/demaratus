from abc import ABC
from redbot.core import Config
from redbot.core.bot import Red
from redbot.core.commands import Cog as COG

class MixinMeta(ABC):
    self.bot: Red
    self.config: Config

class MetaClass(type(COG), type(ABC)):
    pass