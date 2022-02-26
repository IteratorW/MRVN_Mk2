import asyncio
import datetime
import functools
from typing import Optional

from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.permission.decorators import mrvn_guild_only
from api.translation.translatable import Translatable
from extensions.statistics import plot
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsDailyGuildMessages

PLOT_DAYS_COUNT = 30


async def get_monthly_messages(guild_id: int) -> Optional[dict[str, int]]:
    messages = {}

    for day in range(PLOT_DAYS_COUNT):
        date = datetime.date.today() - datetime.timedelta(days=day)

        entries = await StatsDailyGuildMessages.filter(guild_id=guild_id, date=date)

        messages[f"{date.day}-{date.month}"] = 0 if not len(entries) else entries[0].count

    return {k: v for k, v in reversed(list(messages.items()))}


@stats.stats_group.command(description=Translatable("statistics_command_messages_desc"), name="messages")
async def messages_command(ctx: MrvnCommandContext):
    await ctx.defer()

    data = await get_monthly_messages(ctx.guild_id)
    legend_text = ctx.format("statistics_command_messages_legend", ctx.guild.name)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot, data, legend_text))

    await ctx.respond(file=File(result, filename="Chart.png"))
