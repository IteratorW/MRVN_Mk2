from enum import Enum, auto

import discord


class Style(Enum):
    INFO = discord.Embed(title="Info", color=0x3581D8)
    ERROR = discord.Embed(title="Unrecoverable Error", color=0xD82E3F)
    OK = discord.Embed(title="OK", color=0x28CC2D)
    WARN = discord.Embed(title="Warning", color=0xFFE135)
