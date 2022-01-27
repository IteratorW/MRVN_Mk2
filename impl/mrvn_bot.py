import json
from abc import ABC
from collections import defaultdict
from typing import Any

from asciitree import LeftAligned
from discord import Bot, Message, Interaction, InteractionType, SlashCommand, SlashCommandGroup

from api.command.args import element
from api.command.args.arguments import PreparedArguments
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.command.option.ParseUntilEndsOption import ParseUntilEndsOption
from api.embed.style import Style
from api.event_handler import handler_manager
from api.exc import ArgumentParseException


class MrvnBot(Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)

    def get_command_desc(self, command: SlashCommand):
        options = []

        for option in command.options:
            options.append(("<%s>" if option.required else "[%s]") % f"`{option.name}`: *{option.input_type.name}*")

        return f"**{command.name}** {' '.join(options) if len(options) else '*No arguments*'}"

    def get_subcommand_tree(self, command: SlashCommandGroup):
        tree = defaultdict(dict)
        node = tree[f"__{command.name}__"]

        for sub_cmd in command.subcommands:
            if isinstance(sub_cmd, SlashCommandGroup):
                node.update(self.get_subcommand_tree(sub_cmd))
            else:
                node[self.get_command_desc(sub_cmd)] = {}

        return tree

    def get_subcommand_tree_desc(self, command: SlashCommandGroup):
        tr = LeftAligned()

        return tr(self.get_subcommand_tree(command))

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

        orig_cmd = command

        try:
            while isinstance(command, SlashCommandGroup):
                sub_cmd_name = args.next().value

                command = next(filter(lambda it: it.name == sub_cmd_name, command.subcommands))
        except StopIteration:
            await ctx.respond_embed(Style.ERROR, self.get_subcommand_tree_desc(orig_cmd), "Invalid subcommand or group")

            return

        ctx.command = command

        parsers = []

        for option in command.options:
            parser = element.parsers.get(option.input_type, None)

            if parser is None:
                await ctx.respond_embed(Style.ERROR, "This command can not be run with a message. Try a slash command "
                                                     "instead.")

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
                    try:
                        value = parser.parse(ctx, args)
                    except StopIteration:
                        embed = ctx.get_embed(Style.ERROR, title="Not enough arguments")
                        embed.add_field(name=self.get_command_desc(command), value=command.description)

                        await ctx.respond(embed=embed)

                        return

                if len(option.choices) and value not in [x.value for x in option.choices]:
                    choices_desc = "\n".join(["`%s`: **%s**" % (x.name, x.value) for x in option.choices])

                    await ctx.respond_embed(Style.ERROR,
                                            f"The value of {key} is not in choices. Choose one of:\n\n{choices_desc}")

                    return

                kwargs[key] = value
        except ArgumentParseException as e:
            await ctx.respond_embed(Style.ERROR, e.message, "Parsing Error")

            return

        await command(ctx, **kwargs)
