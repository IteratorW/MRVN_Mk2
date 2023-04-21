from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


@runtime.bot.mrvn_command(description=Translatable("tests_command_desc_test_desc"))
async def test_trans_desc(ctx: MrvnContext):
    await ctx.respond_embed(Style.INFO, "B E U")

