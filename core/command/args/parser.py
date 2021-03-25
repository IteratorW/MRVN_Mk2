import abc

from typing import Optional

from core.command.args.arguments import PreparedArguments
from core.command.context import CommandContext


class ParserElement(abc.ABC):
    key: str

    def __init__(self, key: Optional[str]):
        self.key = key

    def parse(self, ctx: CommandContext, args: PreparedArguments):
        try:
            value = self.parse_value(ctx, args)
        except IndexError:
            raise NotImplementedError
        if self.key is not None and value is not None:
            ctx.put_argument(self.key, value)

    @abc.abstractmethod
    def parse_value(self, ctx: CommandContext, args: PreparedArguments):
        pass

    def get_display_usage(self):
        return f"<{self.get_usage()}>"

    @abc.abstractmethod
    def get_usage(self):
        pass
