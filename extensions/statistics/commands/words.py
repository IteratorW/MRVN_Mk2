import datetime
import random
import time

import discord
from discord import Option, OptionChoice

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics import wordcloud_generator
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsChannelMessageTimestamp
from extensions.statistics.wordcloud_generator import NotEnoughInformationError


@stats.stats_group.command(description=Translatable("statistics_command_words_desc"))
async def words(ctx: MrvnCommandContext, shape: Option(str, choices=[OptionChoice("Circle", "circle"),
                                                                     OptionChoice("Triangle", "triangle"),
                                                                     OptionChoice("Pig", "pig"),
                                                                     OptionChoice("BEU", "beu"),
                                                                     OptionChoice("\"Rocket\"", "rocket"),
                                                                     OptionChoice("Random", "random")
                                                                     ]) = "random",
                daily: bool = False, only_from_user: discord.User = None, only_from_channel: discord.TextChannel = None,
                color: Option(str, choices=[
                    OptionChoice("🔵🔵🟣🟣 Cool", "cool"),
                    OptionChoice("🟥🟧🟨🟦 Plasma", "plasma"),
                    OptionChoice("🟢🟣🟨🟨 Viridis", "viridis"),
                    OptionChoice("🟨🟧🟪🟪 Spring", "spring"),
                    OptionChoice("🟨🟨🟤🟤 Spectral", "Spectral"),
                    OptionChoice("🎨💙💚💛 Set3", "Set3"),
                    OptionChoice("🟦⚪🟦⚪ Sea", "PuBu"),
                    OptionChoice("Random", "random")
                ]) = "random"):
    await ctx.defer()

    start_time = time.monotonic()

    try:
        wordcloud_file = await wordcloud_generator.get_wordcloud_file(ctx.guild, shape, color, date=
        None
        if not daily else
        datetime.datetime.utcnow().date(), user=only_from_user, channel=only_from_channel)
    except NotEnoughInformationError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_command_words_error_not_enough_information"))
        return

    if daily:
        title = ctx.translate("statistics_command_words_title_from_today")
    else:
        first_msg_date = await StatsChannelMessageTimestamp.all().order_by('timestamp').first()

        title = ctx.format("statistics_command_words_title_since", first_msg_date.timestamp.strftime("%d.%m.%Y"))

    footer = "\n" + ctx.format("statistics_command_words_elapsed_time", round(time.monotonic() - start_time))

    embed = ctx.get_embed(Style.INFO, title=title)
    embed.set_footer(text=footer)
    embed.set_image(url=f"attachment://{wordcloud_file.filename}")

    await ctx.respond(file=wordcloud_file, embed=embed)
