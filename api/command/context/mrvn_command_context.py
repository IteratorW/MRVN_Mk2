from typing import Union

import discord
from discord import ApplicationContext, Interaction

from api.embed import styled_embed_generator
from api.embed.style import Style


class MrvnCommandContext(ApplicationContext):
    def __init__(self, bot, interaction: Union[Interaction, None]):
        super().__init__(bot, interaction)

    async def respond_embed(self, style: Style, desc: str = None, title: str = None,
                            color: Union[int, discord.Color] = None):
        embed = styled_embed_generator.get_embed(style, desc, title, color,
                                                 self.author if not self.interaction else None, self.guild)

        await self.respond(embed=embed)

    def get_embed(self, style: Style, desc: str = None, title: str = None,
                        color: Union[int, discord.Color] = None) -> discord.Embed:
        embed = styled_embed_generator.get_embed(style, desc, title, color,
                                                 self.author if not self.interaction else None, self.guild)

        return embed
