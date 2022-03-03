import logging
import logging
import traceback
from collections import defaultdict
from typing import Any, Union, Optional, List

from asciitree import LeftAligned
from discord import Message, Interaction, InteractionType, SlashCommand, SlashCommandGroup, UserCommand, \
    MessageCommand, ApplicationCommand, ApplicationCommandInvokeError
from discord import command as create_command
from discord.enums import SlashCommandOptionType

from api.command import categories
from api.command.args import element
from api.command.args.arguments import PreparedArguments
from api.command.command_category import CommandCategory
from api.command.const import PREFIX_LIST, DEFAULT_PREFIX
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.command.mrvn_commands_mixin import MrvnCommandsMixin
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.command.permission.mrvn_permission import MrvnPermission
from api.embed.style import Style
from api.event_handler import handler_manager
from api.exc import ArgumentParseException
from api.models import SettingEnableMessageCommands, CommandOverride, SettingMessageCmdPrefix, \
    SettingAllowCommandsInDMs
from api.translation import translations
from api.translation.translatable import Translatable
from api.translation.translator import Translator
from impl import env

logger = logging.getLogger("MrvnBot")


class MrvnBot(MrvnCommandsMixin):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    @property
    def unique_app_commands(self):
        # For some unknown reason, commands are duplicated in self.application_commands.
        # In some cases, this is unacceptable.

        deduplicated_commands = []

        for cmd in self.application_commands:
            if cmd not in deduplicated_commands:
                deduplicated_commands.append(cmd)

        return deduplicated_commands

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)

    def process_command_translatable_description(self, command: Union[SlashCommand, SlashCommandGroup]):
        if isinstance(command, SlashCommandGroup):
            for cmd in command.subcommands:
                self.process_command_translatable_description(cmd)
        else:
            if isinstance(command.description, Translatable):
                setattr(command, "__mrvn_translatable_desc__", command.description)

                command.description = translations.translate(command.description, translations.FALLBACK_LANGUAGE)

    async def sync_commands(
            self,
            commands: Optional[List[ApplicationCommand]] = None,
            force: bool = False,
            guild_ids: Optional[List[int]] = None,
            register_guild_commands: bool = True,
            unregister_guilds: Optional[List[int]] = None,
    ) -> None:
        if commands is None:
            commands = self.pending_application_commands

        for command in commands:
            if isinstance(command, (SlashCommand, SlashCommandGroup)):
                self.process_command_translatable_description(command)

        await super().sync_commands(commands, True, guild_ids, register_guild_commands, unregister_guilds)

    def process_attributes(self, command: Union[SlashCommand, SlashCommandGroup], **kwargs):
        discord_permissions = kwargs.get("discord_permissions", [])
        owners_only = kwargs.get("owners_only", False)
        guild_only = True if len(discord_permissions) else kwargs.get("guild_only", False)
        category = kwargs.get("category", categories.uncategorized)

        if owners_only or len(discord_permissions):
            setattr(command, "__mrvn_perm__", MrvnPermission(discord_permissions, owners_only))

        setattr(command, "__mrvn_guild_only__", guild_only)
        setattr(command, "__mrvn_category__", category)

    def application_command(self, **kwargs):
        def decorator(func) -> ApplicationCommand:
            result = create_command(**kwargs)(func)
            self.add_application_command(result)

            if isinstance(result, SlashCommand):
                self.process_attributes(result, **kwargs)

            return result

        return decorator

    def create_group(
            self,
            name: str,
            description: Optional[str] = None,
            guild_ids: Optional[List[int]] = None,
            **kwargs
    ) -> SlashCommandGroup:
        command = super().create_group(name, description, guild_ids)

        self.process_attributes(command, **kwargs)

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
            try:
                command = next(filter(lambda it:
                                      isinstance(it, (SlashCommand, SlashCommandGroup, UserCommand, MessageCommand)) and
                                      it.name == interaction.data["name"] and
                                      (bool(len(env.debug_guilds)) or
                                       not it.guild_ids or
                                       interaction.data.get("guild_id", None) in it.guild_ids),
                                      self.application_commands))
            except StopIteration:
                return

        if interaction.type is InteractionType.auto_complete:
            ctx = await self.get_autocomplete_context(interaction)
            ctx.command = command
            return await command.invoke_autocomplete_callback(ctx)

        ctx = MrvnCommandContext(self, interaction)
        ctx.command = command

        guild_id = ctx.guild_id

        if not guild_id and await self.process_dm(ctx):
            return

        if guild_id:
            override = await CommandOverride.get_or_none(command_name=command.name, guild_id=guild_id)
        else:
            override = None

        test = await self.has_permission(ctx.author, ctx.command, override)

        if not test:
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_command_permission_error"))

            return

        if override and not await self.process_override(ctx, override):
            return

        try:
            await ctx.command.invoke(ctx)
        except ApplicationCommandInvokeError as e:
            if type(e.original) == ArgumentParseException:
                # noinspection PyUnresolvedReferences
                await ctx.respond_embed(Style.ERROR, e.original.message,
                                        ctx.translate("mrvn_core_commands_parse_error"))
            else:
                await self.send_command_exception_message(ctx, e.original)
        else:
            self.dispatch("application_command_completion", ctx)

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

        guild_id = message.guild.id if message.guild else None

        if message.guild:
            await ctx.set_from_guild(guild_id)
        else:
            ctx.set_lang(translations.FALLBACK_LANGUAGE)

        try:
            command = next(filter(lambda it:
                                  isinstance(it, (SlashCommand, SlashCommandGroup)) and
                                  it.name == cmd_name and
                                  (bool(len(env.debug_guilds)) or
                                   not it.guild_ids or
                                   guild_id in it.guild_ids), self.application_commands))

            # Bad code. Maybe. The result of filter should always be of SlashCommand*Group*, but IDE doesn't think so
            assert isinstance(command, (SlashCommand, SlashCommandGroup))
        except StopIteration:
            return

        ctx.command = command

        if not guild_id and await self.process_dm(ctx):
            return

        if guild_id:
            override = await CommandOverride.get_or_none(command_name=command.name, guild_id=guild_id)

            override_prefix = override and override.prefix == prefix

            if not override_prefix and prefix != (await SettingMessageCmdPrefix.get_or_create(guild_id=ctx.guild_id))[
                0].value:
                return
        else:
            override = None

            if prefix != DEFAULT_PREFIX:
                return

        if not await self.has_permission(ctx.author, ctx.command, override):
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_command_permission_error"))

            return
        elif override and not await self.process_override(ctx, override):
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
                        embed.add_field(name=self.get_command_desc(command, ctx),
                                        value=self.get_translatable_desc(command, ctx))

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
                        embed.add_field(name=self.get_command_desc(command, ctx),
                                        value=self.get_translatable_desc(command, ctx))

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
        else:
            self.dispatch("application_command_completion", ctx)

    async def process_override(self, ctx: MrvnCommandContext, override: CommandOverride) -> bool:
        if override.disabled:
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_override_command_disabled"))
            return False
        elif len(override.whitelist_channel_ids) and ctx.channel_id not in override.whitelist_channel_ids:
            channel_list = ", ".join([channel.mention if (channel := self.get_channel(x)) else str(x) for x in
                                      override.whitelist_channel_ids])

            await ctx.respond_embed(Style.ERROR,
                                    ctx.format("mrvn_core_override_cant_run_in_this_channel", channel_list))
            return False

        return True

    async def process_dm(self, ctx: MrvnCommandContext):
        allow_dms = (await SettingAllowCommandsInDMs.get_or_create())[0].value

        if not allow_dms:
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_dm_commands_disabled"))
            return True

        guild_only = self.is_guild_only(ctx.command)

        if guild_only:
            await ctx.respond_embed(Style.ERROR, ctx.translate("mrvn_core_command_is_guild_only"))

        return guild_only

    def get_category_commands(self, category: CommandCategory, guild_id: int = None) -> list[ApplicationCommand]:
        commands = []

        for cmd in self.unique_app_commands:
            if not isinstance(cmd, (SlashCommand, SlashCommandGroup)) or not hasattr(cmd,
                                                                                     "__mrvn_category__") or getattr(
                    cmd, "__mrvn_category__") != category:
                continue

            if guild_id:
                if cmd.guild_ids and guild_id not in cmd.guild_ids:
                    continue
            else:
                if not len(env.debug_guilds) and cmd.guild_ids or self.is_guild_only(cmd):
                    continue

            if isinstance(cmd, SlashCommand):
                commands.append(cmd)
            elif isinstance(cmd, SlashCommandGroup):
                commands.extend(self.get_sub_commands(cmd))

        commands = list(commands)

        sub_cmds = []

        for cmd in commands:
            if isinstance(cmd, SlashCommandGroup):
                sub_cmds.extend(self.get_sub_commands(cmd))

        commands.extend(sub_cmds)

        return commands

    @staticmethod
    async def send_command_exception_message(ctx: MrvnCommandContext, exc):
        logger.error(traceback.format_exc())

        await ctx.respond_embed(Style.ERROR,
                                ctx.format("mrvn_api_command_execution_error_desc", "".join(
                                    traceback.format_exception(value=exc, etype=type(exc), tb=exc.__traceback__))),
                                ctx.translate("mrvn_api_command_execution_error_title"))
