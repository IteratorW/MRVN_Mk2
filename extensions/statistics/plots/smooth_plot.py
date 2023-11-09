import asyncio
import datetime
import io
from collections import defaultdict
from datetime import timedelta

import discord
import matplotlib
import numpy as np
from matplotlib import ticker, pyplot as plt
from scipy.stats import gaussian_kde

from extensions.statistics.models import StatsChannelMessageTimestamp
from extensions.statistics import utils


def get_smooth_plot(kde_by_channel, period, guild) -> io.BytesIO:
    ax: matplotlib.axes.Axes
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.linspace(
        (datetime.datetime.now() - period).timestamp(),
        datetime.datetime.now().timestamp(), 1000)

    for channel_id, kde in kde_by_channel.items():
        line = ax.plot(x, kde(x))[0]

        utils.make_line_glow(line, ax)

        line.set_label(guild.get_channel_or_thread(channel_id).name)

    # plt.xticks(rotation=15) #  Bring this back if text doesn't fit

    if period < timedelta(minutes=1):
        dt_format = "%S"
    elif period < timedelta(hours=1):
        dt_format = "%M:%S"
    elif period < timedelta(days=1):
        dt_format = "%H:%M:%S"
    elif period < timedelta(days=31):  # hardcoded month duration
        dt_format = "%m-%d %H:%M:%S"
    else:
        dt_format = "%Y-%m-%d %H:%M:%S"

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: datetime.datetime.fromtimestamp(x).strftime(dt_format)))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1),
              ncol=5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=False)
    buf.seek(0)

    return buf


async def get_smooth_stats(guild: discord.Guild, period_days: float = 1, max_channels: int = 5) -> io.BytesIO:
    period = datetime.timedelta(days=period_days)

    res: list[StatsChannelMessageTimestamp] = \
        await StatsChannelMessageTimestamp.filter(guild_id=guild.id,
                                                  timestamp__gte=(datetime.datetime.now() - period))

    by_channel: dict[int, list[StatsChannelMessageTimestamp]] = defaultdict(list)

    for item in res:
        by_channel[item.channel_id].append(item)

    # PyCharm issue
    # https://youtrack.jetbrains.com/issue/PY-38897
    # noinspection PyTypeChecker
    by_channel = dict(sorted(by_channel.items(), key=lambda x: len(x[1]), reverse=True)[:max_channels])

    event: StatsChannelMessageTimestamp

    kde_by_channel = {
        channel_id: gaussian_kde([event.timestamp.timestamp() for event in events])
        for channel_id, events in by_channel.items()
        if len(events) > 1
    }

    return await asyncio.get_event_loop().run_in_executor(None, get_smooth_plot, kde_by_channel, period, guild)
