from enum import Enum

from discord import Embed


class Style(Enum):
    INFO = Embed(title="mrvn_api_embed_info", color=0x3581D8)
    ERROR = Embed(title="mrvn_api_embed_error", color=0xD82E3F)
    OK = Embed(title="mrvn_api_embed_ok", color=0x28CC2D)
    WARN = Embed(title="mrvn_api_embed_warning", color=0xFFE135)
