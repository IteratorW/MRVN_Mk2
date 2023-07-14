import datetime
import io

import matplotlib.axes
import mplcyberpunk

from collections import defaultdict
from datetime import timedelta
# noinspection PyPackageRequirements
import matplotlib.pyplot as plt
# noinspection PyPackageRequirements
import numpy as np
# noinspection PyPackageRequirements
from discord import File
from matplotlib import ticker
# noinspection PyPackageRequirements
from scipy.stats import gaussian_kde

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsChannelMessageTimestamp

PLOT_DAYS_COUNT = 1


async def get_kde(guild_id: int):
    res: list[StatsChannelMessageTimestamp] = \
        await StatsChannelMessageTimestamp.filter(guild_id=guild_id,
                                                  timestamp__gte=
                                                  (datetime.datetime.now() - datetime.timedelta(days=PLOT_DAYS_COUNT)))

    by_channel: dict[int, list[StatsChannelMessageTimestamp]] = defaultdict(list)

    for item in res:
        by_channel[item.channel_id].append(item)

    # PyCharm issue
    # https://youtrack.jetbrains.com/issue/PY-38897
    # noinspection PyTypeChecker
    by_channel = dict(sorted(by_channel.items(), key=lambda x: len(x[1]), reverse=True)[:5])

    event: StatsChannelMessageTimestamp
    kde_by_channel = {
        channel_id: gaussian_kde([event.timestamp.timestamp() for event in events])
        for channel_id, events in by_channel.items()
        if len(events) > 1
    }

    return kde_by_channel


@stats.stats_group.command(description=Translatable("statistics_command_smooth_desc"), name="smooth")
async def smooth(ctx: MrvnCommandContext):
    await ctx.defer()

    period = datetime.timedelta(days=PLOT_DAYS_COUNT)

    kde_by_channel = await get_kde(ctx.guild_id)

    ax: matplotlib.axes.Axes
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.linspace(
        (datetime.datetime.now() - period).timestamp(),
        datetime.datetime.now().timestamp(), 1000)

    for channel_id, kde in kde_by_channel.items():
        line = ax.plot(x, kde(x))[0]
        line.set_label(ctx.guild.get_channel_or_thread(channel_id).name)

    plt.xticks(rotation=45)

    if period < timedelta(minutes=1):
        dt_format = "%S"
    elif period < timedelta(hours=1):
        dt_format = "%M:%S"
    elif period < timedelta(days=1):
        dt_format = "%H:%M:%S"
    elif period < timedelta(days=31): # hardcoded month duration
        dt_format = "%m-%d %H:%M:%S"
    else:
        dt_format = "%Y-%m-%d %H:%M:%S"


    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: datetime.datetime.fromtimestamp(x).strftime(dt_format)))
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    await ctx.respond(file=File(buf, filename="Chart.png"))
