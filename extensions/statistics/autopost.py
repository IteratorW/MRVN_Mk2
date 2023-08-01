import asyncio
import datetime
import functools
import logging
import traceback

import discord
import openai
from discord import File
from tortoise.expressions import RawSQL
from tortoise.functions import Count

from api.event_handler.decorators import event_handler
from api.extension import extension_manager
from api.models import SettingGuildLanguage
from api.translation.translator import Translator
from extensions.openai import env
from extensions.statistics import plot, wordcloud_generator
from extensions.statistics.commands import channels, messages, smooth, users
from extensions.statistics.models import SettingChannelStatsAutopostEnable, StatsChannelMessageTimestamp
from extensions.statistics.wordcloud_generator import NotEnoughInformationError
from impl import runtime

AI_TITLE_PROMPT_TEXT = \
    """
Статистика каналов по количеству сообщений:
%s
Статистика пользователей по количеству их сообщений:
%s
Ты бот на Discord сервере. Твоя задача - написать небольшой текст, который описывает полученную тобой
статистику выше. Используй не более 5 предложений.
Текст должен быть смешным и саркастическим. Ты должен сравнить статистику каналов и пользователей
за оба дня. Можешь пошутить про участников сервера которые указаны в статистике и каналы, которые укаазны
в статистике.
В свой ответ кроме текста ничего не пиши.
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


# ================================================================== #
# AI


async def get_users_top(guild: discord.Guild, date: datetime.date):
    counts = await StatsChannelMessageTimestamp \
        .annotate(count=Count("id"), date=RawSQL("DATE(timestamp)")) \
        .filter(date=date, guild_id=guild.id) \
        .exclude(user_id=-1) \
        .group_by("user_id") \
        .order_by("-count") \
        .limit(5) \
        .values("count", "user_id")

    counts = [x for x in counts if (member := guild.get_member(x["user_id"])) is None or not member.bot]

    return f"{date.strftime('%d.%m.%Y')}\n" + "\n".join([
        f"{i}. {str(x['user_id']) if (member := guild.get_member(x['user_id'])) is None else member.mention} "
        f"- {x['count']}"
        for i, x in enumerate(counts)])


async def get_channels_top(guild: discord.Guild, date: datetime.date):
    counts = await StatsChannelMessageTimestamp \
        .annotate(count=Count("id"), date=RawSQL("DATE(timestamp)")) \
        .filter(date=date, guild_id=guild.id) \
        .group_by("channel_id") \
        .order_by("-count") \
        .limit(5) \
        .values("count", "channel_id")

    return f"{date.strftime('%d.%m.%Y')}\n" + "\n".join(
        [
            f"{i}. {str(x['channel_id']) if (channel := guild.get_channel(x['channel_id'])) is None else channel.mention} - {x['count']}"
            for i, x in enumerate(counts)])


async def get_ai_prompt(guild: discord.Guild) -> str:
    date_last_day = datetime.date.today() - datetime.timedelta(days=1)
    date_last_last_day = date_last_day - datetime.timedelta(days=1)

    chan_top = f"{await get_channels_top(guild, date_last_day)}\n{await get_channels_top(guild, date_last_last_day)}"
    user_top = f"{await get_users_top(guild, date_last_day)}\n{await get_users_top(guild, date_last_last_day)}"

    return AI_TITLE_PROMPT_TEXT % (chan_top, user_top)


async def prompt_ai_stats_title(guild: discord.Guild):
    import openai

    response_text = (await openai.ChatCompletion.acreate(
        model=env.openai_model,
        messages=[{"role": "user", "content": await get_ai_prompt(guild)}],
        temperature=1.0
    ))["choices"][0]["message"]["content"]

    return response_text


# ================================================================== #


async def send_plot_to_channel(channel: discord.TextChannel):
    title = None

    if "openai" in extension_manager.extensions:
        try:
            title = await prompt_ai_stats_title(channel.guild)
        except openai.OpenAIError:
            logger.error(f"Failed to generate an AI title for autopost, guild {channel.guild.name}")
            logger.error(traceback.format_exc())

            title = None

        if title is not None:
            title = title.replace("\"", "")  # Remove quotes from AI

    lang = (await SettingGuildLanguage.get_or_create(guild_id=channel.guild.id))[0].value
    tr = Translator(lang)

    if title is None:
        title = tr.translate("stats_daily_stats_title")

    # ===========

    files = [
        (await channels.get_channel_stats_file(channel.guild)),
        (await messages.get_messages_stats_file(channel.guild, tr)),
        (await smooth.get_smooth_stats_file(channel.guild)),
        (await users.get_users_stats_file(channel.guild))
    ]

    try:
        files.append(await wordcloud_generator.get_wordcloud_file(channel.guild, "circle",
                                                                  date=datetime.date.today() - datetime.timedelta(
                                                                      days=1)))
    except NotEnoughInformationError:
        pass

    await channel.send(files=files, content=title, allowed_mentions=
    discord.AllowedMentions(users=False, roles=False, everyone=False))


@event_handler()
async def on_startup():
    asyncio.ensure_future(schedule_task())
