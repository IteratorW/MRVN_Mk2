from typing import Union

from discord import Guild, Color, Embed, User

from api.embed.style import Style
from api.translation.translator import Translator


def get_embed(style: Style, desc: str = None, title: str = None, color: Union[int, Color] = None,
              author: User = None, guild: Guild = None,
              translator: Translator = Translator()) -> Embed:
    embed: Embed = style.value.copy()

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
