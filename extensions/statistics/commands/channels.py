import asyncio
import datetime
import functools
import random
from collections import defaultdict
from typing import Optional

import discord
from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics import plot
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsDailyGuildChannelMessages

PLOT_DAYS_COUNT = 30


async def get_last_month_channels_stats(guild: discord.Guild) -> tuple[list[str], dict[str, list[int]]]:
    dates = []
    counts = defaultdict(list)

    for day in reversed(range(PLOT_DAYS_COUNT)):
        date = datetime.date.today() - datetime.timedelta(days=day)
        dates.append(f"{date.day}-{date.month}")

        entries = {}

        for entry in await StatsDailyGuildChannelMessages.filter(guild_id=guild.id, date=date):
            name = chan.name if (chan := guild.get_channel(entry.channel_id)) is not None else str(entry.channel_id)

            entries[name] = entry.count

        for name, count in entries.items():
            if len(counts[name]) == 0:
                counts[name].extend([0] * (PLOT_DAYS_COUNT - 1 - day))

            counts[name].append(count)

        for key in counts.keys():
            if key not in entries:
                counts[key].append(0)

    # Sort
    counts = {k: v for k, v in sorted(counts.items(), reverse=True, key=lambda item: sum(item[1]))}
    # Get top 5
    counts = {k: v for i, (k, v) in enumerate(counts.items()) if i < 5}

    return dates, counts


def get_sample_data() -> tuple[list[str], dict[str, list[int]]]:
    dates = [f"{(date := datetime.date.today() - datetime.timedelta(days=day)).day}-{date.month}" for day in reversed(range(PLOT_DAYS_COUNT))]
    counts = defaultdict(list)

    for i in range(1, 11):
        counts[f"Channel {i}"] = [random.randint(1, 500) for i in range(PLOT_DAYS_COUNT)]

    return dates, counts


async def fill_sample_data():
    c_ids = [610585055684853760, 487020774583042048, 394134985482960907, 1028337603570839673, 574685288996274186]
    g_id = 394132321839874050

    for day in reversed(range(PLOT_DAYS_COUNT)):
        date = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=day), datetime.time())

        for c in c_ids:
            entry = await StatsDailyGuildChannelMessages.get_for_datetime(date, g_id, c)

            entry.count = random.randint(1, 500)

            await entry.save()


async def get_channel_stats_file(guild: discord.Guild) -> discord.File:
    dates, counts = await get_last_month_channels_stats(guild)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot, dates, counts))

    return File(result, filename="Chart_Channels.png")


@stats.stats_group.command(description=Translatable("statistics_command_channels_desc"), name="channels")
async def channels_command(ctx: MrvnCommandContext):
    await ctx.defer()

    await ctx.respond(file=await get_channel_stats_file(ctx.guild))
