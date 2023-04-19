from discord.ext import bridge

from api.command.mrvn_context import MrvnContext
from impl import runtime


@runtime.bot.mrvn_command()
async def test_simple(ctx: MrvnContext):
    await ctx.respond("Test Simple OK")
