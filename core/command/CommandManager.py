from typing import *
from core.command.executor import CommandExecutor
from core.command.specification import CommandSpec
from core.command.args.element import NONE
import logging

logger = logging.getLogger("CommandManager")
commands: List[CommandSpec] = []


def registerCommand(spec):
    """
    Регистрация команды
    :param spec: спецификация команды
    """
    if any(cmd.name == spec.name for cmd in commands):
        raise ValueError(f"Same name \"{spec.name}\" between two commands")
    logger.info(f"Registered command \"{spec.name}\" by module \"{spec.executor.__module__}\"")
    commands.append(spec)


def Command(*aliases: str, arguments=None, short_name: str = "", description: str = "", register=True):
    """
    Регистрация команды
    :param name: название команды
    :param arguments: аргументы команды
    :param register: определяет, нужно ли регистрировать команду. Если False, то возвращает готовую спецификацию команды
    :param short_name: Короткое имя, которое будет отображаться пользователю
    :param description: Краткое описание команды
    :return:
    """
    if arguments is None:
        arguments = NONE
    def decorator(executor: Type[CommandExecutor]):
        spec = CommandSpec(aliases=aliases, executor=executor(), arguments=arguments, short_name=short_name,
                           description=description)
        if register:
            registerCommand(spec)
        return spec

    return decorator
