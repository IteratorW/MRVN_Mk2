import datetime
import os.path
import re
from collections import defaultdict
from io import BytesIO

import discord
import numpy as np
from PIL import ImageEnhance, ImageFilter, Image
from tortoise.expressions import RawSQL
from wordcloud import WordCloud

from extensions.statistics.models import StatsChannelMessageTimestamp

MODULE_PATH = os.path.dirname(__file__)

with open(os.path.join(MODULE_PATH, "wordcloud_stopwords.txt"), "r", encoding="utf-8") as f:
    STOP_WORDS = f.read().split("\n")


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

    records = await StatsChannelMessageTimestamp \
        .annotate(**({"date": RawSQL("DATE(timestamp)")} if daily else {})) \
        .filter(guild_id=guild.id, **({"date": datetime.date.today()} if daily else {})) \
        .exclude(text="") \
        .values("text") \

    freqs = defaultdict(lambda: 0)

    for record in records:
        for word in record["text"].split(" "):
            word = re.sub(r'\W+', '', word.lower().strip())
            if len(word) < 2 or word in STOP_WORDS:
                continue

            freqs[word] += 1

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

