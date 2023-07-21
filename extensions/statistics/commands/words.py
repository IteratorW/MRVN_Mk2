import random

from discord import Option, OptionChoice

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics import wordcloud_generator
from extensions.statistics.commands import stats


@stats.stats_group.command(description=Translatable("statistics_command_words_desc"))
async def words(ctx: MrvnCommandContext, shape: Option(str, choices=[OptionChoice("Circle", "circle"),
                                                                     OptionChoice("Triangle", "triangle"),
                                                                     OptionChoice("Pig", "pig"),
                                                                     OptionChoice("BEU", "beu"),
                                                                     OptionChoice("\"Rocket\"", "rocket"),
                                                                     OptionChoice("Random", "random")]) = "random",
                daily: bool = False):
    await ctx.defer()

    if shape == "random":
        shape = random.choice(["circle", "triangle", "pig", "beu", "rocket"])

    try:
        wordcloud_file = await wordcloud_generator.get_wordcloud_file(ctx.guild, shape, daily)
    except ValueError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_command_words_error_not_enough_information"))
        return

    await ctx.respond(file=wordcloud_file)

