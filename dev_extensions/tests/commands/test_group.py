from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime

test_group = runtime.bot.create_mrvn_group("test_group")


@test_group.command()
async def sub1(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Subcommand #1")


@test_group.command()
async def sub2(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "Subcommand #2")
