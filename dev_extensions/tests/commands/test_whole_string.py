from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
async def test_whole_string(ctx: MrvnContext, *, query: str):
    await ctx.respond_embed(Style.INFO, f"Test Query: {query}")
