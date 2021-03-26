from typing import Union, List

import discord

from core import CommandExecutor, CommandContext, Command, PermissionContext, Arguments, CommandSpec, CommandManager, \
    CommandResult, event


class PermCtx(PermissionContext):
    def should_be_executed(self, ctx: CommandContext) -> bool:
        return ctx.message.author.id == 308653925379211264

    def requirements(self, ctx: CommandContext) -> Union[List[discord.Permissions], str]:
        return "Хуй тебе"

    def should_be_found(self, ctx: CommandContext, spec: "CommandSpec") -> bool:
        return True


@Command("child", arguments=[Arguments.singleString("test")], register=False)
class TestChildCommand(CommandExecutor):
    async def execute(self, ctx: CommandContext):
        await ctx.message.channel.send("Аргумент: %s" % ctx.get_one("test"))

@Command("child2", register=False)
async def TestChildCommand2(ctx: CommandContext) -> CommandResult:
    await ctx.message.channel.send(str(ctx.message.author))
    return CommandResult.EMPTY

print(type(TestChildCommand))
CommandManager.registerCommand(
    CommandSpec.Builder()
        .alias("test")
        .child(TestChildCommand)
        .child(TestChildCommand2)
        .permission_context(PermCtx())
        .build()
)

# Как встроить noinspection в аннотацию?
# noinspection PyUnusedLocal
@event
async def on_ready(client: discord.Client):
    print("Test ready")
