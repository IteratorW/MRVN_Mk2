from discord.ext.commands import dm_only

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
@dm_only()
async def test_dm_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test DM only OK")

