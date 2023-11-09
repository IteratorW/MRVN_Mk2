import datetime
import io

import discord
from PIL import Image, ImageFilter
from asyncpg import Connection
from matplotlib import pyplot as plt, cycler

from impl import runtime


async def get_data(conn: Connection, guild: discord.Guild, date: datetime.date, users: bool):
    target = "user_id" if users else "channel_id"

    data = await conn.fetch(f"""
    SELECT {target}, COUNT(*) as count FROM statschannelmessagetimestamp
    WHERE DATE(timestamp)=$1
    AND guild_id=$2
    GROUP BY {target}
    ORDER BY count DESC
    LIMIT 5
    """, date, guild.id)

    top = {}

    for x in data:
        try:
            name = (await runtime.bot.fetch_user(x[target])).name if users else guild.get_channel_or_thread(x[target]).name
        except (AttributeError, discord.HTTPException):
            name = f"N/A {str(x[target])[:4]}"

        top[name] = x["count"]

    return top


def get_plot(data: list[int], colors: list[str] = None) -> Image:
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))

    if colors is not None:
        ax.set_prop_cycle(cycler(color=colors))

    fig.patch.set_facecolor("#00000000")

    wedges, _ = ax.pie(data, wedgeprops=dict(width=0.35))

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches="tight")
    buf.seek(0)
    img = Image.open(buf)

    blurred = img.filter(ImageFilter.GaussianBlur(radius=25))

    final = Image.new("RGBA", (img.width, img.height), color=(0, 0, 0, 0))

    new_width, new_height = img.width - 100, img.height - 100
    smaller = img.resize((new_width, new_height))

    final.paste(blurred, (0, 0), blurred)
    final.paste(smaller, (int(img.width / 2 - new_width / 2), int(img.height / 2 - new_height / 2)), smaller)

    return final
