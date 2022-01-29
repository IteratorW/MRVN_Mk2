from enum import Enum, auto

import discord


class Style(Enum):
    INFO = discord.Embed(title="mrvn_api_embed_info", color=0x3581D8)
    ERROR = discord.Embed(title="mrvn_api_embed_error", color=0xD82E3F)
    OK = discord.Embed(title="mrvn_api_embed_ok", color=0x28CC2D)
    WARN = discord.Embed(title="mrvn_api_embed_warning", color=0xFFE135)
