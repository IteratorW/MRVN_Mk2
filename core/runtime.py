# НЕ ИМПОРТИРОВАТЬ ЭТОТ МОДУЛЬ ВНУТРИ ПАКЕТА CORE

import discord
import os
from core import CommandContext, Message, CommandManager

client = discord.Client()
globals()["client"] = client
def start():
    for directory in os.environ.get("SEARCH_DIRECTORIES").split(","):
        for module in os.listdir(directory):
            __import__(f"{directory}.{module}", globals(), locals())
    client.run(os.environ.get("DISCORD_TOKEN"))