from typing import *

from core.command.result import CommandResult
from core.command.context import CommandContext
from core.command.executor import CommandExecutor
from core.command.specification import CommandSpec
from core.command.args.element import NONE, seq
from core.command.context import PermissionContext
import logging

logger = logging.getLogger("CommandManager")
commands: List[CommandSpec] = []


def registerCommand(spec: CommandSpec):
    """
    Регистрация команды
    :param spec: спецификация команды
    """
    for command in commands:
        interdiction = set(command.aliases).intersection(set(spec.aliases))
        if interdiction:
            raise ValueError(
                f"Commands {command.aliases[0]} and {spec.aliases[0]} have interdiction in aliases: {interdiction}")
    logger.info(f"Registered command \"{spec.aliases[0]}\"")
    commands.append(spec)


def Command(*aliases: str,
            register=True,
            arguments=None,
            short_name: str = "",
            description: str = "",
            permission_context: PermissionContext = PermissionContext.Default(),
            prefix=None
            ) -> \
        Callable[
            [ # То, что принимает
                Union[
                    Type[CommandExecutor],
                    Callable[
                        ["CommandContext"], # То, что принимает
                        "CommandResult" # То, что отдает
                    ]
                ]
            ],
            CommandSpec]: # То, что отдает
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
    """
    if arguments is None:
        arguments = NONE
    else:
        arguments = seq(arguments)

    if arguments is None:
        arguments = NONE

    def decorator(executor: Union[
        Type[CommandExecutor],
        Callable[["CommandContext"], "CommandResult"]
    ]) -> CommandSpec:
        if isinstance(executor, type):
            executor = executor()
        spec = CommandSpec(aliases=aliases, executor=executor, arguments=arguments, short_name=short_name,
                           description=description, children=[], permission_context=permission_context,
                           prefix=prefix)
        if register:
            registerCommand(spec)
        return spec

    return decorator


def abc() -> Callable[[int, int], int]:
    def sum1(a: int, b: int) -> int: return a + b

    return sum1
