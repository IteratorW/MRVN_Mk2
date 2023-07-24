import datetime
import os.path
import re
from collections import defaultdict
from io import BytesIO

import discord
import numpy as np
from PIL import ImageEnhance, ImageFilter, Image
from tortoise import Tortoise
from tortoise.expressions import RawSQL
from wordcloud import WordCloud

from extensions.statistics.models import StatsChannelMessageTimestamp

MODULE_PATH = os.path.dirname(__file__)
WORD_REGEX = re.compile(r"\W+")
NUM_SQL_REQUESTS = 20

with open(os.path.join(MODULE_PATH, "wordcloud_stopwords.txt"), "r", encoding="utf-8") as f:
    STOP_WORDS = set(f.read().split("\n"))


def get_wordcloud_image(data, mask):
    wc = WordCloud(prefer_horizontal=1, scale=3, mode="RGBA", background_color=None,
                   font_path=os.path.join(MODULE_PATH, "wordcloud_font.ttf"), mask=mask, colormap="cool",
                   repeat=False)

    wc.generate_from_frequencies(data)

    return wc.to_image()


def stylize_image(orig):
    blurred = ImageEnhance.Brightness(orig.filter(ImageFilter.GaussianBlur(radius=50))).enhance(2.5)

    final = Image.new("RGBA", (orig.width, orig.height), color="black")

    final.paste(blurred, (0, 0), blurred)

    final.paste(orig, (0, 0), orig)

    return final


async def get_wordcloud_file(guild: discord.Guild, shape: str, daily: bool):
    """
    Gets a Discord file with wordcloud-like statistics of used words for a specified guild.
    If `daily` is True, then only today's messages are accounted for.

    ValueError is raised if there are less than 20 words collected.
    """

    freqs = defaultdict(lambda: 0)

    count = await StatsChannelMessageTimestamp.all().count()

    limit = count // NUM_SQL_REQUESTS

    for i in range(NUM_SQL_REQUESTS):
        offset = i * limit

        sql = f"""
        SELECT text FROM statschannelmessagetimestamp WHERE guild_id={guild.id} AND NOT text='' LIMIT {limit} OFFSET {offset}
        """
        records = (await Tortoise.get_connection("default").execute_query(sql))[1]

        for record in records:
            for word in record["text"].split(" "):
                word = WORD_REGEX.sub("", word.lower())
                if len(word) < 2:
                    continue

                freqs[word] += 1

    freqs = dict(filter(lambda it: it[0] not in STOP_WORDS, freqs.items()))

    if len(freqs) < 20:
        raise ValueError

    # Take only 200 first words, cuz otherwise it's cluttered
    freqs = dict(sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:200])

    # It works tho
    # noinspection PyTypeChecker
    mask = np.array(Image.open(os.path.join(MODULE_PATH, f"wordcloud_masks/mask_{shape}.png")))

    img = stylize_image(get_wordcloud_image(freqs, mask))
    img.save(buf := BytesIO(), format="PNG")
    buf.seek(0)

    return discord.File(buf, "Wordcloud_Chart.png")

