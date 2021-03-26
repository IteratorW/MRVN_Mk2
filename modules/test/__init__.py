from typing import Union, List

import discord

from core import CommandExecutor, CommandContext, Command, PermissionContext, Arguments, CommandSpec


class PermCtx(PermissionContext):
    def should_be_executed(self, ctx: CommandContext) -> bool:
        return ctx.message.author.id == 308653925379211264

    def requirements(self, ctx: CommandContext) -> Union[List[discord.Permissions], str]:
        return "Хуй тебе"

    def should_be_found(self, ctx: CommandContext, spec: "CommandSpec") -> bool:
        return True


@Command("test", arguments=[Arguments.singleString("test")], permission_context=PermCtx())
class TestCommand(CommandExecutor):
    async def execute(self, ctx: CommandContext):
        await ctx.message.channel.send("Аргумент: %s" % ctx.get_one("test"))
