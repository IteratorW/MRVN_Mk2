from typing import Union

import discord

from api.embed.style import Style
from api.translation.translator import Translator


def get_embed(style: Style, desc: str = None, title: str = None, color: Union[int, discord.Color] = None,
              author: discord.User = None, guild: discord.Guild = None,
              translator: Translator = Translator()) -> discord.Embed:
    embed: discord.Embed = style.value.copy()

    if title:
        embed.title = title
    else:
        embed.title = translator.translate(embed.title)

    if desc:
        embed.description = desc

    if color:
        embed.colour = color

    if author:
        embed.set_footer(
            text=translator.format("mrvn_api_embed_requestedby", f"{author.name}#{author.discriminator}"),
            icon_url=author.avatar.url)

    if guild and style == Style.INFO and guild.me.top_role.position != 0:
        embed.colour = guild.me.top_role.colour

    return embed