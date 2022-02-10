import logging
import logging
import traceback
import types
from abc import ABC
from collections import defaultdict
from typing import Any, Union, Dict, Optional, List

from asciitree import LeftAligned
from discord import Bot, Message, Interaction, InteractionType, SlashCommand, SlashCommandGroup, UserCommand, \
    MessageCommand, ApplicationCommand, ApplicationCommandInvokeError, User
from discord import command as create_command
from discord.enums import SlashCommandOptionType

from api.command import categories
from api.command.args import element
from api.command.args.arguments import PreparedArguments
from api.command.command_category import CommandCategory
from api.command.const import PREFIX_LIST
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.command.permission.mrvn_permission import MrvnPermission
from api.embed.style import Style
from api.event_handler import handler_manager
from api.exc import ArgumentParseException
from api.models import SettingEnableMessageCommands, MrvnUser, CommandOverride, SettingMessageCmdPrefix
from api.translation.translator import Translator
from impl import env

logger = logging.getLogger("MrvnBot")


class MrvnBot(Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)

    def slash_command(self, category: CommandCategory = categories.uncategorized, **kwargs):
        return self.application_command(cls=SlashCommand, category=category, **kwargs)

    def application_command(self, **kwargs):
        def decorator(func) -> ApplicationCommand:
            result = create_command(**kwargs)(func)
            self.add_application_command(result)

            if isinstance(result, SlashCommand):
                kwargs.get("category", categories.uncategorized).add_command(result)

            return result

        return decorator

    def create_group(
            self,
            name: str,
            description: Optional[str] = None,
            guild_ids: Optional[List[int]] = None,
            category: CommandCategory = categories.uncategorized,
            discord_permissions: list[str] = None,
            owners_only: bool = False
    ) -> SlashCommandGroup:
        command = super().create_group(name, description, guild_ids)

        category.add_command(command)

        if discord_permissions or owners_only:
            command.__mrvn_perm__ = MrvnPermission(discord_permissions, owners_only=owners_only)

        return command

    def get_subcommand_tree(self, command: SlashCommandGroup, translator: Translator = Translator()):
        tree = defaultdict(dict)
        node = tree[f"__{command.name}__"]

        for sub_cmd in command.subcommands:
            if isinstance(sub_cmd, SlashCommandGroup):
                node.update(self.get_subcommand_tree(sub_cmd, translator))
            else:
                node[self.get_command_desc(sub_cmd, translator)] = {}

        return tree

    def get_command_desc(self, command: Union[SlashCommand, SlashCommandGroup], translator: Translator = Translator(),
                         as_tree=False):
        if isinstance(command, SlashCommand):
            options = []

            for option in command.options:
                options.append((
                                   "<%s>" if option.required else "[%s]") % f"`{option.name}`: *{translator.translate(f'mrvn_core_commands_option_{option.input_type.name}')}*")

            parents = []

            parent = command

            while parent.parent is not None:
                parent = parent.parent

                parents.append(parent.name)

            parents.reverse()

            return f"{' '.join(parents)} **{command.name}** {' '.join(options) if len(options) else translator.translate('mrvn_core_commands_no_args')}"
        else:
            if as_tree:
                return LeftAligned()(self.get_subcommand_tree(command, translator))
            else:
                sub_cmds = []

                for sub_cmd in command.subcommands:
                    if isinstance(sub_cmd, SlashCommandGroup):
                        sub_cmds.append(f"<{self.get_command_desc(sub_cmd, translator)}>")
                    else:
                        sub_cmds.append(sub_cmd.name)

                return f"**{command.name}** <{'|'.join(sub_cmds)}>"

    async def on_interaction(self, interaction: Interaction):
        if interaction.type not in (
                InteractionType.application_command,
                InteractionType.auto_complete
        ):
            return

        try:
            command = self._application_commands[interaction.data["id"]]
        except KeyError:
            for cmd in self.application_commands:
                if (
                        isinstance(cmd, (SlashCommand, UserCommand, MessageCommand))
                        and cmd.name == interaction.data["name"]
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
        override = await CommandOverride.get_or_none(command_name=command.name, guild_id=ctx.guild_id)

        if not await self.check_permissions(ctx, override):
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_command_permission_error"))

            return

        if override and not await self.check_override(ctx, override):
            return

        try:
            await ctx.command.invoke(ctx)
        except ApplicationCommandInvokeError as e:
            if type(e.original) == ArgumentParseException:
                await ctx.respond_embed(Style.ERROR, e.original.message,
                                        ctx.translate("mrvn_core_commands_parse_error"))
            else:
                await self.send_command_exception_message(ctx, e.original)

    async def on_message(self, message: Message):
        if message.webhook_id or message.author.bot or not message.content or message.content[0] not in PREFIX_LIST:
            return

        prefix = message.content[0]

        if message.guild is not None and not env.debug:
            setting = (await SettingEnableMessageCommands.get_or_create(guild_id=message.guild.id))[0]

            if not setting.value:
                return

        args = PreparedArguments(message.content)
        cmd_name = args.next().value[1:].lower()

        ctx = MrvnMessageContext(self, message)
        await ctx.set_from_guild(message.guild)

        for cmd in self.application_commands:
            if isinstance(cmd, (
                    SlashCommand, SlashCommandGroup)) and cmd.name == cmd_name and message.guild.id in cmd.guild_ids:
                command = cmd
                break
        else:
            return

        ctx.command = command
        override = await CommandOverride.get_or_none(command_name=command.name, guild_id=ctx.guild_id)

        override_prefix = False

        if override and override.prefix == prefix:
            override_prefix = True

        if not override_prefix and prefix != (await SettingMessageCmdPrefix.get_or_create(guild_id=ctx.guild_id))[0].value:
            return

        if not await self.check_permissions(ctx, override):
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_command_permission_error"))

            return

        if override and not await self.check_override(ctx, override):
            return

        try:
            while isinstance(command, SlashCommandGroup):
                sub_cmd_name = args.next().value

                command = next(filter(lambda it: it.name == sub_cmd_name, command.subcommands))
        except StopIteration:
            await ctx.respond_embed(Style.ERROR, self.get_command_desc(ctx.command, ctx, as_tree=True),
                                    ctx.translate("mrvn_core_commands_subcommand_error"))

            return

        ctx.command = command

        options = command.options
        parsers = []

        for option in options:
            parser = element.parsers.get(option.input_type, None)

            if parser is None and option.input_type != SlashCommandOptionType.attachment:
                await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_commands_slash_only"))

                return

            parsers.append(parser)

        kwargs = {}

        attachment_index = 0

        try:
            for i, parser in enumerate(parsers):
                option = options[i]
                key = option.name

                if option.input_type == SlashCommandOptionType.attachment:
                    try:
                        kwargs[key] = message.attachments[attachment_index]
                    except IndexError:
                        await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_commands_attach_error"),
                                                ctx.translate("mrvn_core_commands_parse_error"))

                        return

                    attachment_index += 1

                    continue

                if isinstance(option, ParseUntilEndsOption):
                    values = []

                    if not args.has_next():
                        embed = ctx.get_embed(Style.ERROR,
                                              title=ctx.translate("mrvn_core_commands_arguments_not_enough"))
                        embed.add_field(name=self.get_command_desc(command, ctx), value=command.description)

                        await ctx.respond(embed=embed)

                        return

                    while args.has_next():
                        values.append(parser.parse(ctx, args))

                    kwargs[key] = " ".join([str(x) for x in values])

                    break

                if not option.required:
                    if key in args.keys:
                        value = parser.parse(ctx, args.keys[key], translator=ctx)
                    else:
                        value = option.default
                else:
                    try:
                        value = parser.parse(ctx, args, translator=ctx)
                    except StopIteration:
                        embed = ctx.get_embed(Style.ERROR,
                                              title=ctx.translate("mrvn_core_commands_arguments_not_enough"))
                        embed.add_field(name=self.get_command_desc(command, ctx), value=command.description)

                        await ctx.respond(embed=embed)

                        return

                if option.input_type == SlashCommandOptionType.string and (converter := option.converter) is not None:
                    value = await converter.convert(converter, ctx, value)

                if len(option.choices) and value not in [x.value for x in option.choices]:
                    choices_desc = "\n".join(["`%s`: **%s**" % (x.name, x.value) for x in option.choices])

                    await ctx.respond_embed(Style.ERROR,
                                            ctx.format("mrvn_core_commands_not_in_choices", value, choices_desc))

                    return

                kwargs[key] = value
        except ArgumentParseException as e:
            await ctx.respond_embed(Style.ERROR, e.message, ctx.translate("mrvn_core_commands_parse_error"))

            return

        try:
            await command(ctx, **kwargs)
        except Exception as e:
            await self.send_command_exception_message(ctx, e)

    async def is_owner(self, user: User) -> bool:
        mrvn_user = await MrvnUser.get_or_none(user_id=user.id)

        if not mrvn_user:
            return False

        return mrvn_user.is_owner

    async def check_permissions(self, ctx: MrvnCommandContext, override: CommandOverride = None):
        obj = ctx.command if isinstance(ctx.command, SlashCommandGroup) else ctx.command.callback

        mrvn_perm: MrvnPermission = getattr(obj, "__mrvn_perm__", None)

        if mrvn_perm and mrvn_perm.owners_only:
            return await self.is_owner(ctx.author)
        elif override and len(override.discord_permissions):
            perms = override.discord_permissions
        elif mrvn_perm:
            perms = mrvn_perm.discord_permissions
        else:
            return True

        for k, v in iter(ctx.author.guild_permissions):
            if k in perms and not v:
                return False

        return True

    async def check_override(self, ctx: MrvnCommandContext, override: CommandOverride) -> bool:
        if override.disabled:
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_override_command_disabled"))
            return False
        elif len(override.whitelist_channel_ids) and ctx.channel_id not in override.whitelist_channel_ids:
            channel_list = ", ".join([channel.mention if (channel := self.get_channel(x)) else str(x) for x in
                                      override.whitelist_channel_ids])

            await ctx.respond_embed(Style.ERROR, ctx.format("mrvn_core_override_cant_run_in_this_channel", channel_list))
            return False

        return True

    @staticmethod
    async def send_command_exception_message(ctx: MrvnCommandContext, exc):
        logger.error(traceback.format_exc())

        await ctx.respond_embed(Style.ERROR,
                                ctx.format("mrvn_api_command_execution_error_desc", "".join(
                                    traceback.format_exception(value=exc, etype=type(exc), tb=exc.__traceback__))),
                                ctx.translate("mrvn_api_command_execution_error_title"))
