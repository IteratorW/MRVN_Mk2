import discord

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
@discord.option("style", choices=["INFO", "ERROR", "OK", "WARN"])
async def test_styled(ctx: MrvnContext, style: str):
    await ctx.respond_embed(getattr(Style, style), f"Styled embed {style} test OK!")
