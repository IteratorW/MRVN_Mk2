import asyncio
import datetime
import io

import discord
import matplotlib.dates
import numpy as np
from matplotlib import pyplot as plt, cycler
from tortoise import Tortoise

from extensions.statistics import utils

NUM_DAYS = 30


def get_plot(x: list[datetime.date], counts: list[tuple[list[int], str | None]], draw_trend_line: bool = False,
             colors: list[str] = None):
    """
    A generic plot function, used to make message counts statistics (users, channels and overall messages stats)

    :param x: X-axis list - the dates.
    :param counts: Y-axis. A tuple with y data and optional name.
    :param draw_trend_line: Draw or not draw the trend line. Note: trend line is shown only if one Y axis is provided.
    :param colors: Custom colors for lines
    :return: PNG image BytesIO
    """

    fig, ax = plt.subplots(figsize=(12, 6))

    if colors is not None:
        ax.set_prop_cycle(cycler(color=["BCD2EE", "00FF51", "D90368", "4444FF", "FFFF00"]))

    for y, name in counts:
        line = ax.plot(x, y, marker="o")[0]

        if name:
            line.set_label(name)

        utils.make_line_glow(line, ax)

    # Trend Line ================

    if len(counts) == 1 and draw_trend_line:
        np_array = np.array(counts[0][0])
        x_numbers = list(range(len(x)))

        z = np.polyfit(x_numbers, np_array, 1)
        p = np.poly1d(z)

        line = ax.plot(x, p(x_numbers), "--", color="#00ff41")[0]
        utils.make_line_glow(line, ax)

    # Legend ====================

    if len(counts) == 1:
        plt.legend([counts[0][1]])
    else:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1),
                  ncol=5)

    # Plot Config ===============

    max_y = max([max(x[0]) for x in counts])

    ax.set_ylim([0, max_y + 10])
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m.%d"))
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=1))

    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    return buf


async def get_messages_stats(guild: discord.Guild) -> io.BytesIO:
    async with Tortoise.get_connection("default").acquire_connection() as conn:
        data = await conn.fetch(f"""
        SELECT DATE(timestamp) as date, COUNT(*) FROM statschannelmessagetimestamp
        WHERE guild_id=$1
        AND DATE(timestamp) > (CURRENT_DATE - INTERVAL '{NUM_DAYS + 1} day') AND DATE(timestamp) < CURRENT_DATE
        GROUP BY date
        ORDER BY date ASC
        """, guild.id)

    data = {x["date"]: x["count"] for x in data}

    # fill in the missing dates if there are any
    if len(data) < NUM_DAYS:
        d = list(data.keys())
        date_set = set(d[0] + datetime.timedelta(x) for x in range((d[-1] - d[0]).days))

        data.update({k: 0 for k in sorted(date_set - set(d))})

        data = dict(sorted(data.items(), key=lambda item: item[0]))

    x = list(data.keys())

    return await asyncio.get_event_loop().run_in_executor(None, get_plot, x, [(list(data.values()), guild.name)], True)
