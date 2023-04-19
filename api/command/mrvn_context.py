import abc
from abc import ABC
from typing import Union

from discord import Color, Embed, ApplicationContext, Message
from discord.ext.bridge import BridgeExtContext, BridgeContext, BridgeApplicationContext

from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation import translations
from api.translation.translator import Translator


class MrvnContext(BridgeContext, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tr = Translator()

    async def respond_embed(self, style: Style, desc: str = None, title: str = None,
                            color: Union[int, Color] = None, **kwargs: object) -> object:
        embed = self.get_embed(style, desc, title, color)

        return await self.respond(embed=embed, **kwargs)

    @abc.abstractmethod
    def get_embed(self, style: Style, desc: str = None, title: str = None,
                  color: Union[int, Color] = None) -> Embed:
        pass


class MrvnPrefixContext(MrvnContext, BridgeExtContext):
    def get_embed(self, style: Style, desc: str = None, title: str = None, color: Union[int, Color] = None) -> Embed:
        embed = styled_embed_generator.get_embed(style, desc, title, color,
                                                 self.author,
                                                 self.guild,
                                                 self.tr)

        return embed

    # Override default behaviour: force message sending instead of replying to the author on context respond.
    async def _respond(self, *args, **kwargs) -> Message:
        kwargs.pop("ephemeral", None)
        message = await self._get_super("channel").send(*args, **kwargs)
        if self._original_response_message is None:
            self._original_response_message = message
        return message


class MrvnApplicationContext(MrvnContext, BridgeApplicationContext):
    def get_embed(self, style: Style, desc: str = None, title: str = None, color: Union[int, Color] = None) -> Embed:
        embed = styled_embed_generator.get_embed(style, desc, title, color,
                                                 None,
                                                 self.guild,
                                                 self.tr)

        return embed
