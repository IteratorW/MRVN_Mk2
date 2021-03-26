import abc
from core.command.context import CommandContext

class CommandExecutor(abc.ABC):
    @abc.abstractmethod
    async def execute(self, ctx: CommandContext):
        pass

    def __call__(self, ctx: CommandContext):
        return self.execute(ctx)