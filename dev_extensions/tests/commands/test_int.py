import discord

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
async def test_int(ctx: MrvnContext, integer: int):
    await ctx.respond_embed(Style.INFO, f"Integer argument test: {integer}")
