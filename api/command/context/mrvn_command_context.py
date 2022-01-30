from typing import Union

import discord
from discord import ApplicationContext, Interaction

from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation.translator import Translator


class MrvnCommandContext(ApplicationContext, Translator):
    def __init__(self, bot, interaction: Union[Interaction, None]):
        super().__init__(bot, interaction)

        self.set_from_interaction(interaction)

    async def respond_embed(self, style: Style, desc: str = None, title: str = None,
                            color: Union[int, discord.Color] = None, **kwargs):
        embed = self.get_embed(style, desc, title, color)

        await self.respond(embed=embed, **kwargs)

    def get_embed(self, style: Style, desc: str = None, title: str = None,
                  color: Union[int, discord.Color] = None) -> discord.Embed:
        embed = styled_embed_generator.get_embed(style, desc, title, color,
                                                 self.author if not self.interaction else None, self.guild,
                                                 self)

        return embed
