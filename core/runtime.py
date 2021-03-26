# НЕ ИМПОРТИРОВАТЬ ЭТОТ МОДУЛЬ ВНУТРИ ПАКЕТА CORE
import sys
from typing import List

import discord
import os
import logging
import traceback
from core.events import callbacks
from core import CommandManager, CommandSpec, PreparedArguments, CommandContext
from core.exception import ArgumentParseException, CommandException

PREFIX = os.environ.get("PREFIX")

logger = logging.getLogger("Core")
client = discord.Client()


# globals()["client"] = client
def start():
    logger.info("Importing modules")
    ignored_modules = set(os.getenv("IGNORED_MODULES", "").split(","))
    for directory in os.environ.get("SEARCH_DIRECTORIES").split(","):
        for module in os.listdir(directory):
            module = f"{directory}.{module}"
            if module in ignored_modules:
                continue
            logging.info(f"Importing module \"{module}\"")
            try:
                __import__(f"{module}", globals(), locals())
            except Exception as e:
                logger.error("Error importing module")
                traceback.print_exc(file=sys.stderr)
    logger.info("Logging into discord..")
    client.run(os.environ.get("DISCORD_TOKEN"))


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    logger.info("Initializing modules")
    for callback in callbacks["on_ready"]:
        callback: callable
        logger.info(f"Initializing module {callback.__module__}")
        try:
            await callback(client)
        except Exception as e:
            logger.error("Error initializing module", exc_info=e)
    logger.info("Finished")


@client.event  # TODO заменить всё на эмбеды
async def on_message(message: discord.Message):
    # Не забудь про core/languages.py, кидай туда все тексты сообщений и импортируй здесь
    # Для команд делай свой модуль languages в пап очке
    if message.author.bot or isinstance(message, discord.WebhookMessage):
        return
    content: str = message.content
    if content.startswith(PREFIX):
        prefix = PREFIX
    else:
        spec = next(
            filter(lambda spec: spec.prefix is not None and content.startswith(spec.prefix), CommandManager.commands),
            None)
        if spec is None:
            return
        prefix = spec.prefix
    args = PreparedArguments(content)
    cmd = args.next().value[len(prefix):].lower()
    ctx = CommandContext(message)
    command = next(filter(lambda spec: (not spec.prefix or spec.prefix == prefix)
                                       and next(filter(lambda x: x.lower() == cmd, spec.aliases), None)
                                       and spec.permission_context.should_be_found(ctx, spec),
                          CommandManager.commands), None)
    if command is None:
        # СУКА АЛЕ ТАЙПХИНТЫ ГДЕ
        channel: discord.TextChannel = message.channel
        await channel.send("Команда не найдена")  # TODO
        return
    ctx.specification = command

    rootCommand = command
    commandTree: List[CommandSpec] = [command]

    while command.has_child() and args.has_next():
        next_arg = args.next().value
        command = next(
            filter(
                lambda spec: any(alias.lower() == next_arg.lower() for alias in spec.aliases),
                command.children
            ), None
        )
        if not command: break
        commandTree.append(command)

    for command_ in commandTree:
        if not command_.permission_context.should_be_executed(ctx):
            # Внимание, оно может вернуть список discord.Permissions
            await message.channel.send(f"Нет прав! Необходимые права:\n{command.permission_context.requirements(ctx)}")
            return
    del command_

    if command.has_child():
        await message.channel.send(
            "Ошибка подбора дочерней команды\nНевозможно найти подходящую дочернюю команду\n" +
            prefix + " ".join(spec.aliases[0] for spec in commandTree) +  # Вот это забери как билдер строки юзания
            " <" + "|".join(spec.aliases[0] for spec in command.children) + ">\n" +
            rootCommand.description)
        return
    try:
        command.arguments.parse(ctx, args)
    except ArgumentParseException as e:
        await message.channel.send(
            f"Ошибка разбора аргументов\n{e.message}\n" +
            prefix + " ".join(spec.aliases[0] for spec in commandTree) + # Вот это забери как билдер строки юзания
            " " + command.arguments.get_display_usage() + "\n" +
            rootCommand.description)
        return
    logger.info(f"Executing command {command.aliases[0]} from {message.author} ({message.author.id})")
    try:
        result = await command.executor(ctx)
    except CommandException as e:
        await message.channel.send(f"Произошла ошибка при выполнении команды: {e.message}")
    except Exception:
        logger.error("Exception during command execution")
        traceback.print_exc(file=sys.stderr)
        await message.channel.send("Произошла неизвестная ошибка.\nДетали записаны в журнал.")
