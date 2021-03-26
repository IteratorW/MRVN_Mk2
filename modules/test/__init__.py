from core import CommandExecutor, CommandContext, Message, Command

@Command("test")
class TestCommand(CommandExecutor):
    def execute(self, ctx: CommandContext):
        return Message(content="Test response")
