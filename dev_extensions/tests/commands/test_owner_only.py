from discord.ext.commands import is_owner

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
@is_owner()
async def test_owner_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test owner only OK")

