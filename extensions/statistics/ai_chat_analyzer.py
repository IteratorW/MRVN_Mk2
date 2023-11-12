import datetime
import logging
import traceback

import discord
import numpy as np
from scipy.stats import gaussian_kde
from tortoise import Tortoise

from api.chatgpt import chatgpt
from extensions.statistics.utils import NotEnoughInformationError

logger = logging.getLogger("ai chat analysis")

AI_PROMPT = """
    Ниже находится список самых активных сообщений за день на сервере Discord. 
    Напиши 4-5 предложений, которые описывают, что обсуждалось на сервере за день.
    Текст должен быть саркастическим, с издевательствами над темами общения.
    Свой текст начни с фразы "С Новым Дном !". ВАЖНО: Не "днём", а "дном"!!!
    %s
"""
USER_TEMPLATE = "Пользователь %s"


async def get_ai_analysis(messages: str) -> str | None:
    try:
        return await chatgpt.request([(AI_PROMPT % messages, None)])
    except chatgpt.ChatGPTError:
        logger.error(f"Failed to produce chat AI analysis:\n{traceback.format_exc()}")
        return None


async def analyze_chat(guild: discord.Guild, date: datetime.date) -> str | None:
    async with Tortoise.get_connection("default").acquire_connection() as conn:
        res = await conn.fetch("""
        SELECT EXTRACT(EPOCH FROM timestamp), user_id, text FROM statschannelmessagetimestamp 
        WHERE DATE(timestamp)=$1
        AND guild_id=$2
        AND NOT text=''
        ORDER BY timestamp ASC
        """, date, guild.id)

    # this might be unoptimized PoS code

    data = {float(x["extract"]): (x["user_id"], x["text"]) for x in res}
    time_list = list(data.keys())

    try:
        kde = gaussian_kde(time_list)
    except ValueError:
        raise NotEnoughInformationError()

    x = np.linspace(
        datetime.datetime(date.year, date.month, date.day, 0, 0).timestamp(),
        datetime.datetime(date.year, date.month, date.day, 23, 59).timestamp(),
        1000
    )

    max_timestamp = x[np.argmax(kde(x))]
    max_index = time_list.index(min(time_list, key=lambda it: abs(it - max_timestamp)))
    num_adjacent = 20

    start = max(0, max_index - num_adjacent)
    end = min(len(time_list), max_index + num_adjacent + 1)

    active_timestamps = time_list[start:end]

    user_ids = {}

    messages = ""
    for timestamp in active_timestamps:
        msg = data[timestamp]

        if msg[0] not in user_ids:
            user_ids[msg[0]] = len(user_ids) + 1

        messages += f"{datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')} {USER_TEMPLATE % user_ids[msg[0]]}: {msg[1]}\n"

    return await get_ai_analysis(messages)
