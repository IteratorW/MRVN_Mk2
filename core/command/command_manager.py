from typing import *
from core.command.executor import CommandExecutor
from core.command.specification import CommandSpec
from core.command.args.element import NONE
from core.command.context import PermissionContext
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


def Command(*aliases: str, register=True, arguments=None, short_name: str = "", description: str = "",
            children: List[CommandSpec] = None, permission_context: PermissionContext = PermissionContext.Default()):
    """
    Регистрация команды

    :param aliases: Алиасы команды
    :param register: Определяет, нужно ли регистрировать команду. Если False, то возвращает готовую спецификацию команды
    :param arguments: Аргументы команды
    :param short_name: Короткое имя, которое будет отображаться пользователю
    :param description: Краткое описание команды
    :param children: Дочерние команды. Несовместимо с аргументами.
    :param permission_context: Контекст прав
    :return:
    """
    if arguments is None:
        arguments = NONE
    if children is None:
        children = []

    def decorator(executor: Type[CommandExecutor]):
        spec = CommandSpec(aliases=aliases, executor=executor(), arguments=arguments, short_name=short_name,
                           description=description, children=children, permission_context=permission_context)
        if register:
            registerCommand(spec)
        return spec

    return decorator
