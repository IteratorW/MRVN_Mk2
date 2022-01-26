import asyncio
import logging

import discord

from api.event_handler import handler_manager
from impl import env
from impl.mrvn_bot import MrvnBot

bot = MrvnBot(description="Test", debug_guilds=env.debug_guilds, intents=discord.Intents.all())


async def run():
    await bot.start(env.token)
