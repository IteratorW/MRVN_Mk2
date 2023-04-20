from discord.ext.bridge import has_permissions

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


# Don't mind the type warning. The library wants us to provide permissions as kwargs, but PyCharm doesn't think so.
@runtime.bot.mrvn_command()
@has_permissions(administrator=True)
async def test_admin_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test admin only OK")


@runtime.bot.mrvn_command()
@has_permissions(kick_members=True)
async def test_moderator_only(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Test moderator only OK")


