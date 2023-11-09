import datetime
import io

import discord
import matplotlib
import numpy as np
from PIL import Image
from asyncpg import Connection
from matplotlib import pyplot as plt, ticker
from scipy.stats import gaussian_kde

from extensions.statistics import utils
from extensions.statistics.utils import NotEnoughInformationError


async def get_data(conn: Connection, guild: discord.Guild, date: datetime.date):
    kde = await conn.fetch("""
    SELECT EXTRACT(EPOCH FROM timestamp) FROM statschannelmessagetimestamp 
    WHERE DATE(timestamp)=$1
    AND guild_id=$2
    """, date, guild.id)

    try:
        return gaussian_kde([float(x["extract"]) for x in kde])
    except ValueError:
        raise NotEnoughInformationError()


async def get_plot(kde, date: datetime.date) -> Image:
    ax: matplotlib.axes.Axes
    fig, ax = plt.subplots(figsize=(15, 7.5))

    ax.yaxis.set_ticklabels([])
    ax.tick_params(axis='x', which='major', labelsize=20)
    ax.grid(linewidth=2)

    fig.patch.set_facecolor("#00000000")

    x = np.linspace(
        datetime.datetime.combine(date, datetime.time.min).timestamp(),
        datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time.min).timestamp(),
        1000
    )

    line = ax.plot(x, kde(x), linewidth=7)[0]

    utils.make_line_glow(line, ax)

    dt_format = "%H:%M"

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: datetime.datetime.fromtimestamp(x).strftime(dt_format)))

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches="tight")
    buf.seek(0)

    return Image.open(buf)
