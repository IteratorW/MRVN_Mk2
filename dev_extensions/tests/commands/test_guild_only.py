from discord.ext.bridge import guild_only

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
@guild_only()
async def test_guild_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test Guild Only OK")

