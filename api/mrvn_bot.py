import difflib
import logging
import re
import traceback

import discord.errors
from discord import Message, Interaction, ApplicationContext, DiscordException, ApplicationCommandInvokeError, User
from discord.ext import bridge
from discord.ext.commands import Context, errors, CommandInvokeError

from api.command.mrvn_command import MrvnCommand
from api.command.mrvn_command_group import MrvnCommandGroup
from api.command.mrvn_context import MrvnPrefixContext, MrvnApplicationContext, MrvnContext
from api.embed.style import Style
from api.models import SettingAllowCommandsInDMs, MrvnUser
from api.translation.translator import Translator


class MrvnCheckError(errors.CheckFailure):
    pass


class MrvnBot(bridge.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.command_prefix = "?"
        self.help_command = None

        self.add_check(self.mrvn_check, call_once=True)

    async def get_context(self, message: Message, cls=None) -> MrvnPrefixContext:
        ctx: MrvnPrefixContext = await super().get_context(message, cls=MrvnPrefixContext)  # type: ignore

        if message.guild is not None:
            await ctx.tr.set_from_guild(message.guild.id)

        return ctx

    async def get_application_context(
            self, interaction: Interaction, cls=None
    ) -> MrvnApplicationContext:
        ctx: MrvnApplicationContext = await super().get_application_context(interaction,  # type: ignore
                                                                            cls=MrvnApplicationContext)
        await ctx.tr.set_from_interaction(interaction)

        return ctx

    def create_mrvn_group(self, name: str):
        result = MrvnCommandGroup(name=name)
        self.add_bridge_command(result)
        return result

    def mrvn_command(self, **kwargs):
        def decorator(func) -> MrvnCommand:
            result = mrvn_command(**kwargs)(func)
            self.add_bridge_command(result)
            return result

        return decorator

    # Command overrides below

    async def is_owner(self, user: User) -> bool:
        result = await super().is_owner(user)

        # App owner or app team member is checked in the super method. If the result is false, check for our owner list.
        if result:
            return True

        mrvn_user = await MrvnUser.get_or_none(user_id=user.id)

        if not mrvn_user:
            return False

        return mrvn_user.is_owner

    async def on_application_command_error(self, ctx: MrvnApplicationContext, exception: DiscordException) -> None:
        await self.process_command_error(ctx, exception)

    async def on_command_error(self, ctx: MrvnPrefixContext, exception: errors.CommandError) -> None:
        await self.process_command_error(ctx, exception)

    async def on_application_command_completion(self, ctx: MrvnPrefixContext | MrvnApplicationContext):
        await self.process_command_completion(ctx)

    async def on_command_completion(self, ctx: MrvnPrefixContext | MrvnApplicationContext):
        await self.process_command_completion(ctx)

    async def process_command_error(self, ctx: MrvnContext, exception: DiscordException | errors.CommandError):
        if isinstance(exception, (CommandInvokeError, ApplicationCommandInvokeError)):
            await self.process_invocation_error(ctx, exception.original)
        elif isinstance(exception, errors.UserInputError):
            await ctx.respond_embed(Style.ERROR, ctx.tr.format("mrvn_core_command_bad_user_input", exception))
        elif isinstance(exception, errors.NoPrivateMessage):
            await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_command_is_guild_only"))
        elif isinstance(exception, errors.NSFWChannelRequired):
            await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_command_is_nsfw_only"))
        elif isinstance(exception, (errors.NotOwner, errors.MissingPermissions)):
            await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_command_permission_error"))
        elif isinstance(exception, errors.PrivateMessageOnly):
            await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_command_is_dm_only"))
        elif isinstance(exception, errors.BotMissingPermissions):
            await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_bot_insufficient_perms"))
        elif isinstance(exception, errors.CommandNotFound):
            await self.process_unknown_command(ctx)
        elif isinstance(exception, MrvnCheckError):
            pass  # The global MRVN check sends out an error message by itself
        else:
            await ctx.respond_embed(Style.ERROR, ctx.tr.format("mrvn_core_command_unknown_library_error", str(exception)))

    @staticmethod
    async def process_invocation_error(ctx: MrvnContext, exc: Exception):
        exc_traceback = "".join(traceback.format_exception(exc))
        logging.error(f"Error while trying to execute command:\n{exc_traceback}")

        await ctx.respond_embed(Style.ERROR,
                                ctx.tr.format("mrvn_api_command_execution_error_desc",
                                              f"||```python\n{exc_traceback}\n```||"),
                                ctx.tr.translate("mrvn_api_command_execution_error_title"))

    @staticmethod
    async def process_command_completion(ctx: MrvnPrefixContext | MrvnApplicationContext):
        message = f"Executed Command /{ctx.command.name} [{'Slash' if ctx.is_app else 'Prefixed'}] "

        if ctx.guild is not None:
            message += f"[Guild {ctx.guild.name}] [Author {ctx.author.id} {ctx.author.name}#{ctx.author.discriminator}]"
        else:
            message += f"[DM {ctx.author.id} {ctx.author.name}#{ctx.author.discriminator}]"

        logging.info(message)

    async def process_unknown_command(self, ctx: MrvnPrefixContext):
        command_name = ctx.invoked_with

        similar_commands = {}
        matcher = difflib.SequenceMatcher(None, command_name)
        for command in [x.name for x in self.commands]:
            matcher.set_seq2(command)

            if (ratio := matcher.ratio()) > 0.5:
                similar_commands[ratio] = ctx.clean_prefix + command

        similar_commands = {k: v for k, v in sorted(similar_commands.items(), reverse=True, key=lambda item: item[0])}
        similar_commands = {k: v for i, (k, v) in enumerate(similar_commands.items()) if i < 3}

        await ctx.respond_embed(
            Style.ERROR,
            ctx.tr.format("mrvn_core_bot_similar_commands", ", ".join(similar_commands.values())) if len(similar_commands) else "",
            ctx.tr.translate("mrvn_core_bot_unknown_command_title"))

    async def mrvn_check(self, ctx: MrvnApplicationContext | MrvnPrefixContext):
        if ctx.guild is None:
            allow_dms = (await SettingAllowCommandsInDMs.get_or_create())[0].value

            if not allow_dms:
                await ctx.respond_embed(Style.ERROR, ctx.tr.translate("mrvn_core_dm_commands_disabled"))
                raise MrvnCheckError()

        return True


def mrvn_command(**kwargs):
    def decorator(callback):
        return MrvnCommand(callback, **kwargs)

    return decorator
