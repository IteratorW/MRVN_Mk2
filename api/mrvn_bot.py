import logging
import traceback

from discord import Message, Interaction, ApplicationContext, DiscordException, ApplicationCommandInvokeError
from discord.ext import bridge
from discord.ext.commands import Context, errors, CommandInvokeError

from api.command.mrvn_command import MrvnCommand
from api.command.mrvn_command_group import MrvnCommandGroup
from api.command.mrvn_context import MrvnPrefixContext, MrvnApplicationContext, MrvnContext
from api.embed.style import Style
from api.translation.translator import Translator


class MrvnBot(bridge.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.command_prefix = "?"
        self.help_command = None

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

    async def on_application_command_error(self, ctx: MrvnApplicationContext, exception: DiscordException) -> None:
        if isinstance(exception, ApplicationCommandInvokeError):
            await self.process_invocation_error(ctx, exception.original)
        else:
            await ctx.respond_embed(Style.ERROR, ctx.tr.format("mrvn_core_command_unknown_library_error", str(exception)))

    async def on_command_error(self, ctx: MrvnPrefixContext, exception: errors.CommandError) -> None:
        if isinstance(exception, CommandInvokeError):
            await self.process_invocation_error(ctx, exception.original)
        elif isinstance(exception, errors.UserInputError):
            await ctx.respond_embed(Style.ERROR, ctx.tr.format("mrvn_core_command_bad_user_input", exception))
        else:
            await ctx.respond_embed(Style.ERROR, ctx.tr.format("mrvn_core_command_unknown_library_error", str(exception)))

    async def on_application_command_completion(self, ctx: MrvnPrefixContext | MrvnApplicationContext):
        await self.process_command_completion(ctx)

    async def on_command_completion(self, ctx: MrvnPrefixContext | MrvnApplicationContext):
        await self.process_command_completion(ctx)

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


def mrvn_command(**kwargs):
    def decorator(callback):
        return MrvnCommand(callback, **kwargs)

    return decorator
