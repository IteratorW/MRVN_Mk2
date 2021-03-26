from typing import *
from core.command.executor import CommandExecutor
from core.command.specification import CommandSpec
from core.command.args.element import NONE, seq
from core.command.context import PermissionContext
import logging

logger = logging.getLogger("CommandManager")
commands: List[CommandSpec] = []


def registerCommand(spec):
    """
    Регистрация команды
    :param spec: спецификация команды
    """
    for command in commands:
        interdiction = set(command.aliases).intersection(set(spec.aliases))
        if interdiction:
            raise ValueError(f"Commands {command.aliases[0]} and {spec.aliases[0]} have interdiction in aliases: {interdiction}")
    logger.info(f"Registered command \"{spec.aliases[0]}\" by module \"{spec.executor.__module__}\"")
    commands.append(spec)


def Command(*aliases: str, register=True, arguments=None, short_name: str = "", description: str = "",
            children: List[CommandSpec] = None, permission_context: PermissionContext = PermissionContext.Default(), prefix=None):
    """
    Регистрация команды


    :param aliases: Алиасы команды
    :param register: Определяет, нужно ли регистрировать команду. Если False, то возвращает готовую спецификацию команды
    :param arguments: Аргументы команды
    :param short_name: Короткое имя, которое будет отображаться пользователю
    :param description: Краткое описание команды
    :param children: Дочерние команды. Несовместимо с аргументами.
    :param permission_context: Контекст прав
    :param prefix: Кастомный префикс команды
    :return:
    """
    if arguments is None:
        arguments = NONE
    if children is None:
        children = []

    def decorator(executor: Type[CommandExecutor]):
        spec = CommandSpec(aliases=aliases, executor=executor(), arguments=seq(arguments), short_name=short_name,
                           description=description, children=children, permission_context=permission_context, prefix=prefix)
        if register:
            registerCommand(spec)
        return spec

    return decorator
