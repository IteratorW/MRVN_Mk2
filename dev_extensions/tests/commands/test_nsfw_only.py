from discord.ext.bridge import guild_only, is_nsfw

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
@is_nsfw()
async def test_nsfw_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test NSFW channel only OK")

