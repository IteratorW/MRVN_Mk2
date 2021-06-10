from typing import List, Optional, Type, Callable, Union

from core.command.context import PermissionContext, CommandContext
from core.command.result import CommandResult
from core.command.executor import CommandExecutor
from core.command.args.parser import ParserElement
from core.command.args.element import seq, NONE


class CommandSpec:
    name: str
    executor: CommandExecutor
    arguments: ParserElement
    short_name: str
    description: str
    children: List["CommandSpec"]
    permission_context: PermissionContext
    prefix = Optional[str]

    def __init__(self, aliases, executor, arguments, short_name, description, children, permission_context, prefix):
        if children:
            if arguments is not NONE:
                raise RuntimeError("Children and arguments in one specification")
            elif executor is not None:
                raise RuntimeError("Children and executor in one specification")
        elif executor is None:
            raise RuntimeError("Executor is None")
        if not aliases:
            raise RuntimeError("Must be at least one alias")
        self.aliases = aliases
        self.executor = executor
        self.arguments = arguments
        self.short_name = short_name
        self.description = description
        self.children = children
        self.permission_context = permission_context
        self.prefix = prefix

    def has_child(self):
        return bool(self.children)

    class Builder:
        def __init__(self):
            self._aliases = []
            self._children = []
            self._executor = None
            self._arguments = NONE
            self._short_name = ""
            self._description = ""
            self._permission_context = PermissionContext.Default()
            self._prefix = None

        def alias(self, alias: str) -> "CommandSpec.Builder":
            """
            :param alias: Алиас, по которому команда будет вызываться
            """
            self._aliases.append(alias)
            return self

        def child(self, child: Union[
            "CommandSpec",  # Сюда подавать можно только это
        ]) -> "CommandSpec.Builder":
            """
            Добавление дочерней команды. Типы Type и Callable добавлены для адекватного тайпчекинга пичармом (Иначе куча ворнов).
            :param child: CommandSpec: Спецификация дочерней команды
            """
            self._children.append(child)
            return self

        def aliases(self, *aliases: str) -> "CommandSpec.Builder":
            """
            :param aliases: Алиасы. по которым команда будет вызываться
            """
            self._aliases = aliases
            return self

        def prefix(self, prefix: str) -> "CommandSpec.Builder":
            self._prefix = prefix
            return self

        def executor(self, executor: Union[
            "CommandExecutor",
            Callable[["CommandContext"], "CommandResult"]]) -> "CommandSpec.Builder":
            """
            :param executor: Исполнитель команды
            """
            self._executor = executor
            return self

        def arguments(self, *args: ParserElement) -> "CommandSpec.Builder":
            """
            :param args: Аргументы команды
            """
            self._arguments = seq(list(args))
            return self

        def permission_context(self, context: PermissionContext) -> "CommandSpec.Builder":
            self._permission_context = context
            return self

        def short_name(self, short_name) -> "CommandSpec.Builder":
            """
            :param short_name: Короткое имя, которое будет отображаться пользователю
            """
            self._short_name = short_name
            return self

        def description(self, description) -> "CommandSpec.Builder":
            """
            :param description: Краткое описание команды
            """
            self._description = description
            return self

        def build(self) -> "CommandSpec":
            return CommandSpec(self._aliases, self._executor, self._arguments, self._short_name, self._description,
                               self._children, self._permission_context, self._prefix)
