from typing import List

from core.command.context import PermissionContext
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

    def __init__(self, aliases, executor, arguments, short_name, description, children, permission_context):
        if children and arguments is not NONE:
            raise RuntimeError("Children and arguments in one specification")
        self.aliases = aliases
        self.executor = executor
        self.arguments = arguments
        self.short_name = short_name
        self.description = description
        self.children = children
        self.permission_context = permission_context

    class Builder:
        def __init__(self):
            self._aliases = []
            self._children = []
            self._executor = None
            self._arguments = NONE
            self._short_name = ""
            self._description = ""
            self._permission_context = PermissionContext.Default()

        def alias(self, alias: str):
            """
            :param alias: Алиас, по которому команда будет вызываться
            """
            self._aliases.append(alias)

        def child(self, child: "CommandSpec"):
            self._children.append(child)

        def aliases(self, *aliases: str):
            """
            :param aliases: Алиасы. по которым команда будет вызываться
            """
            self._aliases = aliases

        def executor(self, executor: "CommandExecutor"):
            """
            :param executor: Исполнитель команды
            """
            self._executor = executor
            return self

        def arguments(self, *args: ParserElement):
            """
            :param args: Аргументы команды
            """
            self._arguments = seq(list(args))
            return self

        def permission_context(self, context: PermissionContext):
            self._permission_context = context

        def short_name(self, short_name):
            """
            :param short_name: Короткое имя, которое будет отображаться пользователю
            """
            self._short_name = short_name
            return self

        def description(self, description):
            """
            :param description: Краткое описание команды
            """
            self._description = description

        def build(self):
            if self._executor is None:
                raise RuntimeError("Executor is None")
            return CommandSpec(self._aliases, self._executor, self._arguments, self._short_name, self._description,
                               self._children, self._permission_context)
