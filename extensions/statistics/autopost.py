import asyncio
import datetime
import functools
import logging
import traceback

import discord
from discord import File

from api.event_handler.decorators import event_handler
from api.extension import extension_manager
from api.models import SettingGuildLanguage
from api.translation.translator import Translator
from extensions.statistics import plot
from extensions.statistics.commands import channels
from extensions.statistics.models import SettingChannelStatsAutopostEnable
from impl import runtime

AI_TITLE_PROMPT_TEXT = \
"""
Сгенерируй заголовок для сообщения о статистики сообщений в каналах Discord сервера за прошедший день.
В заголовок включи следующие слова: "С новым дном!".
Сделай этот заголовок смешным и саркастическим. Можешь пошутить про участников сервера и админа.
"""

logger = logging.getLogger("Statistics auto stats")


async def schedule_task():
    while True:
        dt = datetime.datetime.now()
        tomorrow = dt + datetime.timedelta(days=1)
        seconds_until_new_day = (datetime.datetime.combine(tomorrow, datetime.time.min) - dt).seconds

        if seconds_until_new_day < 1:
            continue

        await asyncio.sleep(seconds_until_new_day)

        await autopost_task()


async def autopost_task():
    entries = await SettingChannelStatsAutopostEnable.filter(value_field=True)

    for entry in entries:
        guild = runtime.bot.get_guild(entry.guild_id)

        if guild is None:
            continue

        sys_channel = guild.system_channel

        if sys_channel is None:
            continue

        try:
            await send_plot_to_channel(sys_channel)
        except Exception:
            logger.error(f"Error sending autopost to guild {guild.name}")
            logger.error(traceback.format_exc())


async def prompt_ai_stats_title():
    import openai

    if openai.api_key is None:
        return None

    try:
        response_text = (await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": AI_TITLE_PROMPT_TEXT}],
            temperature=1.0
        ))["choices"][0]["message"]["content"]

        return response_text
    except openai.OpenAIError:
        return None


async def send_plot_to_channel(channel: discord.TextChannel):
    title = None

    if "openai" in extension_manager.extensions:
        title = await prompt_ai_stats_title()

        if title is not None:
            title = title.replace("\"", "")  # Remove quotes from AI

    if title is None:
        lang = (await SettingGuildLanguage.get_or_create(guild_id=channel.guild.id))[0]

        title = Translator(lang).translate("stats_daily_stats_title")

    # ===========

    dates, counts = await channels.get_last_month_channels_stats(channel.guild)

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(plot.get_plot, dates, counts))

    await channel.send(file=File(result, filename="Chart_Channels.png"), content=title)


@event_handler()
async def on_startup():
    asyncio.ensure_future(schedule_task())
