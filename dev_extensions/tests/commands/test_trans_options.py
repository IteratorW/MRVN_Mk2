from api.command.mrvn_context import MrvnContext
from api.command.mrvn_option import mrvn_option
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


@runtime.bot.mrvn_command()
@mrvn_option("int1", description=Translatable("tests_command_trans_options_option_int1"))
@mrvn_option("str1", description=Translatable("tests_command_trans_options_option_str1"))
@mrvn_option("number1", description=Translatable("tests_command_trans_options_option_number1"))
async def test_trans_options(ctx: MrvnContext, int1: int, str1: str, number1: float):
    await ctx.respond_embed(Style.INFO, ctx.tr.translate("tests_command_trans_options_ok") +
                            f"\n{int1}, {str1}. {number1}")

