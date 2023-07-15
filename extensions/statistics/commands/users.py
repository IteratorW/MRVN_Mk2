import asyncio
import datetime
import functools
from collections import defaultdict

import discord
from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics import plot
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsChannelMessageTimestamp

PLOT_DAYS_COUNT = 30


async def get_last_month_users_stats(guild: discord.Guild) -> tuple[list[str], dict[str, list[int]]]:
    now_date = datetime.datetime.today()

    res: list[StatsChannelMessageTimestamp] = \
        await StatsChannelMessageTimestamp.filter(guild_id=guild.id,
                                                  timestamp__gte=
                                                  (now_date - datetime.timedelta(days=PLOT_DAYS_COUNT)))

    dates = [f"{(date := datetime.date.today() - datetime.timedelta(days=day)).day}-{date.month}" for day in reversed(range(PLOT_DAYS_COUNT))]
    counts = defaultdict(lambda: [0] * PLOT_DAYS_COUNT)

    for entry in res:
        if entry.user_id == -1:
            continue

        member = guild.get_member(entry.user_id)

        if member is None or member.bot:
            continue

        timestamp = entry.timestamp.replace(tzinfo=None)

        counts[member.display_name][(PLOT_DAYS_COUNT - (now_date - timestamp).days) - 1] += 1

    # PyCharm issue
    # https://youtrack.jetbrains.com/issue/PY-38897
    # noinspection PyTypeChecker
    counts = dict(sorted(counts.items(), key=lambda x: sum(x[1]), reverse=True)[:5])

    # Computing sum here for the second time, but who cares....
    counts = {f"{x} ({sum(y)})": y for x, y in counts.items()}

    return dates, counts


@stats.stats_group.command(description=Translatable("statistics_command_users_desc"), name="users")
async def users_command(ctx: MrvnCommandContext):
    await ctx.defer()

    dates, counts = await get_last_month_users_stats(ctx.guild)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot,
                                                                                    dates, counts, None, True))

    await ctx.respond(file=File(result, filename="Chart_Users.png"))
