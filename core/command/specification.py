from core.command.executor import CommandExecutor
from core.command.args.parser import ParserElement
from core.command.args.element import seq, NONE

# TODO PermissionContext

class CommandSpec:
    name: str
    executor: CommandExecutor
    arguments: ParserElement
    short_name: str
    description: str

    def __init__(self, aliases, executor, arguments, short_name, description):
        self.aliases = aliases
        self.executor = executor
        self.arguments = arguments
        self.short_name = short_name
        self.description = description

    class Builder:
        def __init__(self):
            self._aliases = []
            self._executor = None
            self._arguments = NONE
            self._short_name = ""
            self._description = ""

        def alias(self, alias: str):
            """
            :param alias: Алиас, по которому команда будет вызываться
            """
            self._aliases.append(alias)

        def aliases(self, *aliases: str):
            """
            :param aliases: Алиасы. по которым команда будет вызываться
            """
            self._aliases = aliases

        def executor(self, executor: CommandExecutor):
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
            return CommandSpec(self._aliases, self._executor, self._arguments, self._short_name, self._description)