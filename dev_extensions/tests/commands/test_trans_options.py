import discord

from api.command.mrvn_context import MrvnContext
from api.command.mrvn_option_choice import MrvnOptionChoice
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


@runtime.bot.mrvn_command(description=Translatable("tests_command_options_test_desc"))
@discord.option("option", choices=[
    MrvnOptionChoice(Translatable("tests_command_options_test_option_1_name"), "123"),
    MrvnOptionChoice(Translatable("tests_command_options_test_option_2_name"), "test"),
    MrvnOptionChoice(Translatable("tests_command_options_test_option_3_name"), "ORIONHEL")
])
async def test_trans_options(ctx: MrvnContext, option: str):
    await ctx.respond_embed(Style.INFO, ctx.tr.format("tests_command_options_test_response", option))

