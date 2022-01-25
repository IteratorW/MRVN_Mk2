from abc import ABC
from typing import Any

from discord import Bot, Message, Interaction, InteractionType

from api.command.mrvn_command_context import MrvnCommandContext
from api.command.mrvn_message_context import MrvnMessageContext
from api.event_handler import handler_manager


class MrvnBot(Bot, ABC):
    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)

    async def on_interaction(self, interaction: Interaction):
        if interaction.type not in (
                InteractionType.application_command,
        ):
            return

        try:
            command = self._application_commands[interaction.data["id"]]
        except KeyError:
            for cmd in self.application_commands:
                if (
                        cmd.name == interaction.data["name"]
                        and interaction.data.get("guild_id", None) in cmd.guild_ids
                ):
                    command = cmd
                    break
            else:
                return self.dispatch("unknown_command", interaction)
        if interaction.type is InteractionType.auto_complete:
            ctx = await self.get_autocomplete_context(interaction)
            ctx.command = command
            return await command.invoke_autocomplete_callback(ctx)

        ctx = MrvnCommandContext(self, interaction)
        ctx.command = command

        await ctx.command.invoke(ctx)

    async def on_message(self, message: Message):
        # Test code for message command support

        if not message.content.startswith("?"):
            return

        args = message.content.split(" ")
        cmd_name = args.pop(0)[1:]

        for cmd in self.application_commands:
            if (
                    cmd.name == cmd_name
                    and message.guild.id in cmd.guild_ids
            ):
                command = cmd
                break
        else:
            return

        ctx = MrvnMessageContext(self, message)
        ctx.command = command

        await command(ctx, arg_1="Test", arg_2="Anus")
