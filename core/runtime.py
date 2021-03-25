# НЕ ИМПОРТИРОВАТЬ ЭТОТ МОДУЛЬ ВНУТРИ ПАКЕТА CORE

import discord
import os
import core.CommandManager as CommandManager
from core import CommandContext, Message

client = discord.Client()
globals()["client"] = client
def start():
    for directory in os.environ.get("SEARCH_DIRECTORIES").split(","):
        for module in os.listdir(directory):
            __import__(f"{directory}.{module}", globals(), locals())
    result: Message = CommandManager.commands[0].executor.execute(CommandContext())
    print(result.content)
    # client.run(os.environ.get("DISCORD_TOKEN"))