import asyncio
import datetime
import functools
from typing import Optional

from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics import plot
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsDailyGuildChannelMessages

PLOT_DAYS_COUNT = 30


async def get_monthly_messages(guild_id: int) -> tuple[list[str], dict[str, list[int]]]:
    messages = {}

    for day in reversed(range(PLOT_DAYS_COUNT)):
        date = datetime.date.today() - datetime.timedelta(days=day)

        entries = await StatsDailyGuildChannelMessages.filter(guild_id=guild_id, date=date)

        messages[f"{date.day}-{date.month}"] = sum([x.count for x in entries])

    return list(messages.keys()), {"": list(messages.values())}


@stats.stats_group.command(description=Translatable("statistics_command_messages_desc"), name="messages")
async def messages_command(ctx: MrvnCommandContext):
    await ctx.defer()

    dates, counts = await get_monthly_messages(ctx.guild_id)

    legend_text = ctx.format("statistics_command_messages_legend", ctx.guild.name)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot, dates, counts, legend_text))

    await ctx.respond(file=File(result, filename="Chart.png"))
