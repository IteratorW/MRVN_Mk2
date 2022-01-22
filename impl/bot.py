import asyncio
import logging

import discord

from api.discord.custom_bot import CustomBot
from api.event_handler import handler_manager
from impl import env

bot = CustomBot(description="Test")


async def run():
    asyncio.ensure_future(bot.start(token=env.token))

    handler_manager.post("startup")  # TODO this actually starts before discord client is ready to work
