from typing import Union

from discord import TextChannel, Option, SlashCommand, Permissions, AutocompleteContext, SlashCommandGroup
from discord.ext.commands import Converter
from discord.utils import basic_autocomplete

from api.command import categories
from api.command.const import PREFIX_LIST
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.event_handler.decorators import event_handler
from api.exc import ArgumentParseException
from api.models import CommandOverride
from api.translation.translatable import Translatable
from impl import runtime

override_group = runtime.bot.create_group("override", category=categories.bot_management,
                                          discord_permissions=["administrator"])
prefix_group = override_group.create_subgroup("prefix", "Prefix management.")
channel_whitelist = override_group.create_subgroup("channel_whitelist", "Channel whitelist.")
permissions = override_group.create_subgroup("permission", "Command Permissions.")

command_names = set([])


class CommandConverter(Converter[SlashCommand]):
    # For some reason, 3 arguments are being passed from slash commands (the first one is replacing self) I don't know
    # why is this happening, so there are no other ways to actually implement a custom Converter for an option.
    # noinspection PyProtocol
    # noinspection PyMethodOverriding
    @staticmethod
    async def convert(converter, ctx: MrvnCommandContext, argument: str) -> Union[SlashCommand, SlashCommandGroup]:
        try:
            command = next(filter(lambda it: it.name == argument, runtime.bot.application_commands))
        except StopIteration:
            raise ArgumentParseException(ctx.translate("std_command_override_command_not_found"))

        return command


async def command_searcher(ctx: AutocompleteContext):
    return command_names


command_option = Option(str, autocomplete=basic_autocomplete(command_searcher))
command_option.converter = CommandConverter()


@event_handler()
async def startup():
    global command_names

    command_names = set(
        [cmd.name for cmd in runtime.bot.application_commands if isinstance(cmd, (SlashCommand, SlashCommandGroup))])


@override_group.command(description=Translatable("std_command_override_info_desc"))
async def info(ctx: MrvnCommandContext, command: command_option):
    override = await CommandOverride.get_or_none(guild_id=ctx.guild_id, command_name=command.name)

    if not override:
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_override_no_override"))

        return

    empty = ctx.translate("std_command_override_empty")

    enabled = not override.disabled
    prefix = override.prefix if len(override.prefix) else empty
    perm_list = ", ".join(override.discord_permissions) if len(override.discord_permissions) else empty
    channel_list = ", ".join([channel.mention if (channel := runtime.bot.get_channel(x)) else str(x) for x in
                              override.whitelist_channel_ids]) if len(override.whitelist_channel_ids) else empty

    await ctx.respond_embed(Style.INFO,
                            ctx.format("std_command_override_info", enabled, prefix, perm_list, channel_list),
                            ctx.format("std_command_override_info_title", command.name))


@override_group.command(name="set_enabled", description=Translatable("std_command_override_set_enabled_desc"))
async def command_set_enabled(ctx: MrvnCommandContext, command: command_option, enable: bool):
    override = (await CommandOverride.get_or_create(guild_id=ctx.guild_id, command_name=command.name))[0]

    override.disabled = not enable

    await override.save()

    await ctx.respond_embed(Style.OK, ctx.format(
        f"std_command_override_command_{'enabled' if enable else 'disabled'}", command.name))


@prefix_group.command(name="set", description=Translatable("std_command_override_prefix_set_desc"))
async def set_prefix(ctx: MrvnCommandContext, command: command_option, prefix: str):
    if prefix not in PREFIX_LIST:
        await ctx.respond_embed(Style.ERROR, ctx.format("std_command_override_prefix_not_in_list", " ".join(PREFIX_LIST)))
        return

    override = (await CommandOverride.get_or_create(guild_id=ctx.guild_id, command_name=command.name))[0]

    override.prefix = prefix

    await override.save()

    await ctx.respond_embed(Style.OK, ctx.format("std_command_override_prefix_changed", command.name))


@prefix_group.command(name="disable", description=Translatable("std_command_override_prefix_disable_desc"))
async def prefix_disable(ctx: MrvnCommandContext, command: command_option):
    override = (await CommandOverride.get_or_create(guild_id=ctx.guild_id, command_name=command.name))[0]

    override.prefix = ""

    await override.save()

    await ctx.respond_embed(Style.OK, ctx.format("std_command_custom_prefix_disabled", command.name))


async def channel_edit(ctx: MrvnCommandContext, command: SlashCommand, channel: TextChannel, add_: bool):
    override = (await CommandOverride.get_or_create(guild_id=ctx.guild_id, command_name=command.name))[0]

    channel_id = channel.id

    if add_ and channel_id not in override.whitelist_channel_ids:
        override.whitelist_channel_ids.append(channel_id)

        await override.save()
    elif not add_ and channel_id in override.whitelist_channel_ids:
        override.whitelist_channel_ids.remove(channel_id)

        await override.save()

    await ctx.respond_embed(Style.OK, ctx.format(
        f"std_command_override_channel_{'added' if add_ else 'removed'}", channel.mention, command.name))


@channel_whitelist.command(name="add", description=Translatable("std_command_override_channel_add_desc"))
async def channel_add(ctx: MrvnCommandContext, command: command_option, channel: TextChannel):
    await channel_edit(ctx, command, channel, True)


@channel_whitelist.command(name="remove", description=Translatable("std_command_override_channel_remove_desc"))
async def channel_remove(ctx: MrvnCommandContext, command: command_option, channel: TextChannel):
    await channel_edit(ctx, command, channel, False)


async def permissions_edit(ctx: MrvnCommandContext, command: command_option, permission: str, add_: bool):
    permission = permission.lower()

    if permission not in Permissions.VALID_FLAGS.keys():
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_override_invalid_permission"))

        return

    override = (await CommandOverride.get_or_create(guild_id=ctx.guild_id, command_name=command.name))[0]

    if add_ and permission not in override.discord_permissions:
        override.discord_permissions.append(permission)

        await override.save()
    elif not add_ and permission in override.discord_permissions:
        override.discord_permissions.remove(permission)

        await override.save()

    await ctx.respond_embed(Style.OK, ctx.format(
        f"std_command_override_permission_{'added' if add_ else 'removed'}", permission, command.name))


permission_option = Option(str, autocomplete=basic_autocomplete(Permissions.VALID_FLAGS.keys()))


@permissions.command(name="add", description=Translatable("std_command_override_perm_add_desc"))
async def permissions_add(ctx: MrvnCommandContext, command: command_option, permission: permission_option):
    await permissions_edit(ctx, command, permission, True)


@permissions.command(name="remove", description=Translatable("std_command_override_perm_remove_desc"))
async def permissions_remove(ctx: MrvnCommandContext, command: command_option, permission: permission_option):
    await permissions_edit(ctx, command, permission, False)
