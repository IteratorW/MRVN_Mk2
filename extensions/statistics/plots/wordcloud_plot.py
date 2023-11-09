import asyncio
import datetime
import io
import logging
import os.path
import random
from io import BytesIO
from pathlib import Path

import PIL
import discord
import numpy as np
from PIL import ImageEnhance, ImageFilter, Image
from tortoise import Tortoise
from tortoise.backends.asyncpg import AsyncpgDBClient
from wordcloud import WordCloud

from extensions.statistics.utils import NotEnoughInformationError

MODULE_PATH = Path(os.path.dirname(__file__)).parent.absolute()


def add_underglow(orig):
    blurred = ImageEnhance.Brightness(orig.filter(ImageFilter.GaussianBlur(radius=50))).enhance(2.5)

    final = Image.new("RGBA", (orig.width, orig.height), color=(0, 0, 0, 0))

    final.paste(blurred, (0, 0), blurred)

    final.paste(orig, (0, 0), orig)

    return final


def get_wordcloud_image(data, mask, color):
    wc = WordCloud(prefer_horizontal=1, scale=3, mode="RGBA", background_color=None,
                   font_path=os.path.join(MODULE_PATH, "./assets/wordcloud_font.ttf"), mask=mask, colormap=color,
                   repeat=False)

    wc.generate_from_frequencies(data)

    return add_underglow(wc.to_image())


async def get_wordcloud_stats(guild: discord.Guild, shape: str = "random", color: str = "random",
                              date: datetime.date = None, user: discord.User = None,
                              channel: discord.TextChannel = None,
                              return_as_image: bool = False) -> io.BytesIO | PIL.Image.Image:
    """
    Gets a Discord file with wordcloud-like statistics of up to 200 most used words in the guild.
    Messages can be filtered by date, user or channel, if any or more is specified.

    NotEnoughInformationError is raised if there are less than 20 words found.
    """

    if shape == "random":
        shape = random.choice(["circle", "triangle", "pig", "beu", "rocket"])

    if color == "random":
        color = random.choice(["cool", "plasma", "viridis", "spring", "Spectral", "Set3", "PuBu"])

    filters = []

    if date is not None:
        filters.append(f"DATE(timestamp)=''{date.strftime('%Y-%m-%d')}''")

    if user is not None:
        filters.append(f"user_id={user.id}")

    if channel is not None:
        filters.append(f"channel_id={channel.id}")

    # noinspection PyTypeChecker
    conn: AsyncpgDBClient = Tortoise.get_connection("default")

    base_sql = f"""
    SELECT word, nentry FROM ts_stat('
        SELECT to_tsvector(''public.mrvn'', text) FROM statschannelmessagetimestamp
        WHERE guild_id={guild.id}
        {f"AND {' AND '.join(filters)}" if len(filters) else ""}
    ')
    WHERE length(word) > 2
    ORDER BY nentry DESC
    LIMIT 200;
    """

    async with conn.acquire_connection() as db:
        rows = await db.fetch(base_sql)

    if len(rows) < 20:
        raise NotEnoughInformationError

    freqs = {x["word"]: x["nentry"] for x in rows}

    # It works tho
    # noinspection PyTypeChecker
    mask = np.array(Image.open(os.path.join(MODULE_PATH, f"./assets/wordcloud_masks/mask_{shape}.png")))

    img = await asyncio.get_event_loop().run_in_executor(None, get_wordcloud_image, freqs, mask, color)

    if return_as_image:
        return img

    img.save(buf := BytesIO(), format="PNG")
    buf.seek(0)

    return buf
