import asyncio
import datetime
import io
import os
import random
from pathlib import Path

import discord
import glitch_this
from PIL import Image, ImageFont, ImageDraw
from pixelsort import pixelsort
from tortoise import Tortoise

from extensions.statistics.plots import wordcloud_plot
from extensions.statistics import utils
from extensions.statistics.plots.daily import daily_smooth, daily_pie

ASSETS_PATH = os.path.join(Path(os.path.dirname(__file__)).parent.parent.absolute(), "./assets/")

# Constants for drawing =====================================================

# Assets

SPRITES_FILE = f"{ASSETS_PATH}/daily_stats_sprites.png"
SOURCE_REGULAR_FILE = f"{ASSETS_PATH}/daily_stats_source_regular.png"
SOURCE_EVENT_FILE = f"{ASSETS_PATH}/daily_stats_source_event.png"

CARD_FONT = ImageFont.truetype(f"{ASSETS_PATH}/daily_stats_fonts/TacticRoundExd-Med.ttf", 100)
TITLE_FONT = ImageFont.truetype(f"{ASSETS_PATH}/daily_stats_fonts/TacticRound-Bld.ttf", 91)
LIST_FONT = ImageFont.truetype(f"{ASSETS_PATH}/daily_stats_fonts/TacticRound-Blk.ttf", 40)

DEBUG_DRAW_TEXT_BBOXES = False

ASSET_TREND_SIGN_WIDTH = 128
ASSET_TREND_SIGN_HEIGHT = 83

TREND_SIGN_SPACING = 15

CARD_TEXT_X = 258
CARD_TEXT_VERTICAL_PADDING = 80
CARD_TEXT_WIDTH = 470

CARD_MESSAGES_Y = 294 + CARD_TEXT_VERTICAL_PADDING
CARD_USERS_Y = 639 + CARD_TEXT_VERTICAL_PADDING

FOOTER_REGULAR_TEXT_X = 1182
FOOTER_TEXT_X = 2645
FOOTER_REGULAR_TEXT_MAX_WIDTH = 756

FOOTER_EVENT_TEXT_X = 350
FOOTER_EVENT_TEXT_MAX_WIDTH = 1549

PIE_CHART_OFFSET_FROM_EDGE = 185
PIE_CHART_Y = 995

PIE_CHART_BLUR_AMOUNT = 40

LIST_RECTANGLE_WIDTH = 15
LIST_RECTANGLE_HEIGHT = 10
LIST_RECTANGLE_SPACING = 15

LIST_TEXT_LINE_SPACING = 50
LIST_Y = 1198
LIST_OFFSET_FROM_CENTER = 375

SMOOTH_CHART_X = 830
SMOOTH_CHART_Y = 257

WORDCLOUD_Y = 1750
WORDCLOUD_SIZE = 850


# Draw functions ============================================================


def draw_text(ctx: ImageDraw, x: int, y: int, font, text: str, fill=None):
    """
    Draws text same as ImageDraw.text, but eliminates vertical paddings that may occur on some fonts.
    :param fill: text color
    :param ctx: drawing context
    :param x: x
    :param y: y
    :param font: font object
    :param text: text to draw
    :return:
    """
    left, top, right, bottom = font.getbbox(text)

    ctx.text(xy=(x, y - top),
             text=text,
             font=font,
             fill=fill)


def text_bbox(font: ImageFont, text: str) -> tuple[int, int]:
    """
    Returns text bbox, intended to be used when drawing with the function above.
    :param font: font object
    :param text: text to get info about
    :return:
    """

    left, top, right, bottom = font.getbbox(text)

    return right - left, bottom - top


def draw_limited_width_text(ctx: ImageDraw, img: Image, x: int, y: int, max_width: int, font, text: str, fill=None):
    """
    Simply draws text, but allows to specify max width to prevent overflowing by stretching the text.
    :param ctx: image drawing context
    :param img: Image object
    :param x: x
    :param y: y
    :param max_width: text max width
    :param font: font object
    :param text: the text
    :param fill: text color
    :return:
    """
    width, height = text_bbox(font, text)

    temp_img = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    test_ctx = ImageDraw.Draw(temp_img)

    draw_text(test_ctx, 0, 0, font, text, fill=fill)

    debug_color = "blue"

    if width > max_width:
        temp_img = temp_img.resize((max_width, temp_img.height))
        width = max_width

        debug_color = "red"

    img.paste(temp_img, (x, y), temp_img)

    if DEBUG_DRAW_TEXT_BBOXES:
        ctx.rectangle((x, y, x + width, y + height), outline=debug_color)


def limited_text_bbox(max_width: int, font: ImageFont, text: str) -> tuple[int, int]:
    """
    Gets a bounding box for a limited width text. Width will be <= max_width.
    :param max_width: max width for the text
    :param font: font object
    :param text: text
    :return: (width, height)
    """

    width, height = text_bbox(font, text)

    return (max_width if width > max_width else width), height


def scale_to_font(font: ImageFont, width: int, height: int) -> tuple[int, int]:
    new_height = int(font.size / 2)
    new_width = int(new_height * width / height)

    return new_width, new_height


def draw_card_text(ctx: ImageDraw, img: Image, sprites_file: Image, x: int, y: int, max_width: int, font: ImageFont,
                   text: str, trend: bool):
    sign_width, sign_height = scale_to_font(font, ASSET_TREND_SIGN_WIDTH, ASSET_TREND_SIGN_HEIGHT)
    text_width, text_height = limited_text_bbox(max_width - sign_width - TREND_SIGN_SPACING, font, text)
    text_x = x + int(max_width / 2 - (text_width + TREND_SIGN_SPACING + sign_width) / 2)

    sign = sprites_file.crop((
        0 if trend else ASSET_TREND_SIGN_WIDTH,
        0,
        ASSET_TREND_SIGN_WIDTH if trend else ASSET_TREND_SIGN_WIDTH * 2,
        ASSET_TREND_SIGN_HEIGHT)).resize((sign_width, sign_height))

    draw_limited_width_text(ctx, img, text_x, y, text_width, font, text)
    img.paste(sign, (text_x + text_width + TREND_SIGN_SPACING, y + int(text_height / 2 - sign_height / 2)), sign)

    if DEBUG_DRAW_TEXT_BBOXES:
        ctx.rectangle((x, y, x + max_width, y + text_height), outline="green")


def draw_footer_text(img, x, y, max_width: int, font, text):
    width, height = limited_text_bbox(max_width, font, text)

    temp_img = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    temp_ctx = ImageDraw.Draw(temp_img)

    draw_limited_width_text(temp_ctx, temp_img, 0, 0, max_width, font, text, fill=(0, 0, 0, 195))

    img.paste(temp_img, (x, y), temp_img)


def draw_pie_list_text(ctx: ImageDraw, img, x: int, y: int, max_width: int, font, text, color,
                       right_alignment: bool):
    rect_width, rect_height = scale_to_font(font, LIST_RECTANGLE_WIDTH, LIST_RECTANGLE_HEIGHT)
    text_width, text_height = limited_text_bbox(max_width - LIST_RECTANGLE_SPACING - rect_width, font, text)

    rect_x = x + max_width - rect_width if right_alignment \
        else x
    text_x = x + max_width - text_width - rect_width - LIST_RECTANGLE_SPACING if right_alignment \
        else x + LIST_RECTANGLE_SPACING + rect_width

    ctx.rounded_rectangle((rect_x, y, rect_x + rect_width, y + rect_height), fill=f"#{color}", radius=3)
    draw_limited_width_text(ctx, img, text_x, y, text_width, font, text)

    if DEBUG_DRAW_TEXT_BBOXES:
        ctx.rectangle((x, y, x + max_width, y + text_height), outline="white")


# Image processing functions =====================================================


def glitch_image(image):
    # Scale down the image so the process won't take a long time
    image = image.resize((int(image.width / 2), int(image.height / 2)))
    image = pixelsort(image, randomness=10, angle=50)
    image = glitch_this.ImageGlitcher().glitch_image(image, glitch_amount=2, scan_lines=False, color_offset=True)

    return image


def hue_shift_image(image, hue_shift: int):
    """
    Shifts hue of the entire image.
    :param image: Image object
    :param hue_shift: The amount to shift (0-255)
    :return:
    """
    hsv = image.convert('HSV')

    h, s, v = hsv.split()

    h = h.point(lambda p: p - hue_shift)

    hsv_r = Image.merge('HSV', (h, s, v))

    rgb_r = hsv_r.convert('RGB')

    return rgb_r


# Image generation =====================================================


def populate_daily_stats(
        messages_count: int,
        users_count: int,
        messages_trend: bool,
        users_trend: bool,
        date_text: str,
        users_top: dict[str, int],
        channels_top: dict[str, int],
        smooth_stats_image,
        wordcloud_image,
        hue_shift: int = 0,
        event: bool = False,
        glitches: bool = False
) -> io.BytesIO:
    image = Image.open(SOURCE_EVENT_FILE if event else SOURCE_REGULAR_FILE)

    if not event and hue_shift != 0:
        image = hue_shift_image(image, hue_shift)

    draw = ImageDraw.Draw(image)

    sprites = Image.open(SPRITES_FILE)

    draw_card_text(draw, image, sprites, CARD_TEXT_X, CARD_MESSAGES_Y, CARD_TEXT_WIDTH, CARD_FONT, str(messages_count),
                   messages_trend)
    draw_card_text(draw, image, sprites, CARD_TEXT_X, CARD_USERS_Y, CARD_TEXT_WIDTH, CARD_FONT, str(users_count),
                   users_trend)

    footer_text_max_width = FOOTER_EVENT_TEXT_MAX_WIDTH if event else FOOTER_REGULAR_TEXT_MAX_WIDTH
    footer_text_actual_width, _ = limited_text_bbox(footer_text_max_width, TITLE_FONT, date_text)
    footer_text_x = FOOTER_EVENT_TEXT_X if event else FOOTER_REGULAR_TEXT_X

    draw_footer_text(image, footer_text_x + int(footer_text_max_width / 2 - footer_text_actual_width / 2),
                     FOOTER_TEXT_X,
                     footer_text_max_width,
                     TITLE_FONT,
                     date_text)

    chart_channels = daily_pie.get_plot(list(channels_top.values()))
    image.paste(chart_channels, (PIE_CHART_OFFSET_FROM_EDGE, PIE_CHART_Y), chart_channels)

    chart_users = daily_pie.get_plot(list(users_top.values()), utils.COLORS_ALTERNATE)
    image.paste(chart_users, (image.width - PIE_CHART_OFFSET_FROM_EDGE - chart_channels.width, PIE_CHART_Y),
                chart_users)

    x_center = int(image.width / 2)

    channel_list_x = x_center - LIST_OFFSET_FROM_CENTER

    for i, channel_name in enumerate(channels_top.keys()):
        draw_pie_list_text(draw, image, channel_list_x, LIST_Y + (i * LIST_TEXT_LINE_SPACING),
                           x_center - channel_list_x, LIST_FONT, channel_name, utils.COLORS_REGULAR[i], False)

    for i, user_name in enumerate(users_top.keys()):
        draw_pie_list_text(draw, image, x_center, LIST_Y + (i * LIST_TEXT_LINE_SPACING), LIST_OFFSET_FROM_CENTER,
                           LIST_FONT, user_name, utils.COLORS_ALTERNATE[i], True)

    image.paste(smooth_stats_image, (SMOOTH_CHART_X, SMOOTH_CHART_Y), smooth_stats_image)

    wordcloud_image = wordcloud_image.resize((WORDCLOUD_SIZE, WORDCLOUD_SIZE))
    wordcloud_x = int(image.width / 2 - WORDCLOUD_SIZE / 2)
    image.paste(wordcloud_image, (wordcloud_x, WORDCLOUD_Y), wordcloud_image)

    if glitches:
        image = glitch_image(image)

    image.save(buf := io.BytesIO(), format="PNG")
    buf.seek(0)

    return buf


# Data requests =====================================================


async def get_count_for_date(conn, guild: discord.Guild, date: datetime.date, users: bool) -> int:
    data = await conn.fetchrow(
        f"""
        SELECT {'COUNT(DISTINCT user_id)' if users else 'COUNT(*)'} FROM statschannelmessagetimestamp
        WHERE guild_id=$1
        AND date(timestamp)=$2
        """, guild.id, date
    )

    return data["count"]


async def get_date_event_text(conn, guild: discord.Guild, date: datetime.date) -> str | None:
    new_date = date.replace(year=1900) + datetime.timedelta(days=1)

    data = await conn.fetchrow("""
    SELECT text FROM statsevententry
    WHERE guild_id=$1
    AND event_date=$2
    """, guild.id, new_date)

    return data["text"] if data is not None else None


async def get_daily_chart_for_date(guild: discord.Guild, date: datetime.date):
    async with Tortoise.get_connection("default").acquire_connection() as conn:
        messages_day = await get_count_for_date(conn, guild, date, False)
        messages_prev_day = await get_count_for_date(conn, guild, date - datetime.timedelta(days=1), False)
        messages_trend = messages_day > messages_prev_day

        users_day = await get_count_for_date(conn, guild, date, True)
        users_prev_day = await get_count_for_date(conn, guild, date - datetime.timedelta(days=1), True)
        users_trend = users_day > users_prev_day

        channels_top = await daily_pie.get_data(conn, guild, date, False)
        users_top = await daily_pie.get_data(conn, guild, date, True)

        smooth_stats_image = await daily_smooth.get_plot(await daily_smooth.get_data(conn, guild, date), date)

        date_event_text = await get_date_event_text(conn, guild, date)

    wordcloud_image = await wordcloud_plot.get_wordcloud_stats(guild, "circle", "cool", date, return_as_image=True)

    hue_shift = int((200 / 7) * (date.weekday() + 1)) - 85
    date_text = date.strftime("%d.%m.%Y")

    should_glitch = random.random() < 0.05

    return await asyncio.get_event_loop().run_in_executor(None, populate_daily_stats,
                                                          messages_day,
                                                          users_day,
                                                          messages_trend,
                                                          users_trend,
                                                          date_text if date_event_text is None else date_event_text,
                                                          users_top,
                                                          channels_top,
                                                          smooth_stats_image,
                                                          wordcloud_image,
                                                          hue_shift,
                                                          date_event_text is not None,
                                                          should_glitch
                                                          )
