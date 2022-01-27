from abc import ABC
from typing import Any

from discord import Bot, Message, Interaction, InteractionType, SlashCommand, SlashCommandGroup

from api.command.args import element
from api.command.args.arguments import PreparedArguments
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.command.option.ParseUntilEndsOption import ParseUntilEndsOption
from api.event_handler import handler_manager
from api.exc import ArgumentParseException


class MrvnBot(Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

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

        args = PreparedArguments(message.content)
        cmd_name = args.next().value[1:].lower()

        for cmd in self.application_commands:
            if isinstance(cmd, (
                    SlashCommand, SlashCommandGroup)) and cmd.name == cmd_name and message.guild.id in cmd.guild_ids:
                command = cmd
                break
        else:
            return

        ctx = MrvnMessageContext(self, message)

        try:
            while isinstance(command, SlashCommandGroup):
                sub_cmd_name = args.next().value

                command = next(filter(lambda it: it.name == sub_cmd_name, command.subcommands))
        except StopIteration:
            await ctx.respond("Invalid subcommand or subcommand group.")

            return

        ctx.command = command

        parsers = []

        for option in command.options:
            parser = element.parsers.get(option.input_type, None)

            if parser is None:
                await ctx.respond(f"Error: could not find parser for slash option type {option.input_type}")

                return

            parsers.append(parser)

        kwargs = {}

        try:
            for i, parser in enumerate(parsers):
                option = command.options[i]
                key = option.name

                if isinstance(option, ParseUntilEndsOption):
                    values = []

                    while args.has_next():
                        values.append(parser.parse(ctx, args))

                    kwargs[key] = " ".join([str(x) for x in values])

                    break

                if not option.required:
                    if key in args.keys:
                        value = parser.parse(ctx, args.keys[key])
                    else:
                        value = option.default
                else:
                    value = parser.parse(ctx, args)

                if value not in [x.value for x in option.choices]:
                    choices_desc = "\n".join(["%s: %s" % (x.name, x.value) for x in option.choices])

                    await ctx.respond(f"The value of {key} is not in choices. Choose one of:\n{choices_desc}")

                    return

                kwargs[key] = value
        except ArgumentParseException as e:
            await ctx.respond(e.message)

            return

        await command(ctx, **kwargs)
