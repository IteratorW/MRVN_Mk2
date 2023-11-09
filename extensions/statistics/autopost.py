import asyncio
import datetime
import logging
import traceback

import discord

from api.event_handler.decorators import event_handler
from api.models import SettingGuildLanguage
from api.translation.translator import Translator
from extensions.statistics import ai_chat_analyzer

from extensions.statistics.models import SettingChannelStatsAutopostEnable
from extensions.statistics.plots.daily import daily_stats
from extensions.statistics.utils import NotEnoughInformationError
from impl import runtime

logger = logging.getLogger("Statistics auto stats")


async def post_daily_message(channel: discord.TextChannel):
    print(datetime.datetime.now())
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    title = await ai_chat_analyzer.analyze_chat(channel.guild, yesterday)
    daily_image = await daily_stats.get_daily_chart_for_date(channel.guild, yesterday)

    if title is None:
        title = Translator((await SettingGuildLanguage.get_or_create(guild_id=channel.guild.id))[0].value).translate(
            "stats_daily_stats_title"
        )

    await channel.send(content=title,
                       file=discord.File(daily_image, f"daily_stats_{yesterday.strftime('%d_%m_%Y')}.png"))


async def schedule_task():
    while True:
        dt = datetime.datetime.now()
        tomorrow = dt + datetime.timedelta(days=1)

        # add a couple of seconds to make sure we're on the new day for sure
        seconds_until_new_day = (datetime.datetime.combine(tomorrow, datetime.time.min) - dt).seconds + 5

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
            await post_daily_message(sys_channel)
        except NotEnoughInformationError:
            pass
        except Exception:
            logger.error(f"Error sending autopost to guild {guild.name} | {guild.id}")
            logger.error(traceback.format_exc())


# ================================================================== #


@event_handler()
async def on_startup():
    asyncio.ensure_future(schedule_task())
