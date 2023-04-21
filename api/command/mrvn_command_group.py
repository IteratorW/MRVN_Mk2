from discord.ext.bridge import BridgeCommandGroup, BridgeExtGroup, BridgeSlashGroup
from discord.ext.commands import Context

from api.command.mrvn_command import MrvnCommand, MrvnPrefixCommand, MrvnSlashCommand
from api.command.mrvn_context import MrvnContext, MrvnPrefixContext
from api.embed.style import Style
from api.translation import translations
from api.translation.translatable import Translatable


class MrvnCommandGroup(BridgeCommandGroup):
    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs):
        self.translatable_description: Translatable | None = None

        if isinstance((desc := kwargs.get("description", None)), Translatable):
            self.translatable_description = desc
        elif desc is None:
            self.translatable_description = Translatable("mrvn_api_command_no_desc")

        # Translate to fallback language
        if self.translatable_description is not None:
            kwargs["description"] = self.translatable_description.translate()

        self.ext_variant: MrvnPrefixGroup = (ext_var := MrvnPrefixGroup(self.custom_callback, *args, **kwargs))
        self.slash_variant: MrvnSlashGroup = MrvnSlashGroup(
            self.custom_callback,
            kwargs.pop("name", ext_var.name),
            *args,
            translatable_description=self.translatable_description,
            **kwargs)
        self.parent = kwargs.pop("parent", None)

        self.subcommands: list[MrvnCommand] = []

    # Override default behaviour: send unknown subcommand message if no valid subcommand is provided.
    async def custom_callback(self, ctx: MrvnContext):
        await ctx.respond_embed(Style.ERROR, "Unknown subcommand!")

    def command(self, *args, **kwargs):
        def wrap(callback):
            translatable_description: Translatable | None = None

            if isinstance((desc := kwargs.get("description", None)), Translatable):
                translatable_description = desc
            elif desc is None:
                translatable_description = Translatable("mrvn_api_command_no_desc")

            # Translate to fallback language
            if translatable_description is not None:
                kwargs["description"] = translatable_description.translate()

            slash = self.slash_variant.command(
                *args,
                translatable_description=translatable_description,
                **kwargs,
                cls=MrvnSlashCommand,
            )(callback)
            ext = self.ext_variant.command(
                *args,
                **kwargs,
                cls=MrvnPrefixCommand,
            )(callback)
            command = MrvnCommand(
                callback, parent=self, slash_variant=slash, ext_variant=ext
            )
            self.subcommands.append(command)
            return command

        return wrap


class MrvnPrefixGroup(BridgeExtGroup):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self.invoke_without_command = True


class MrvnSlashGroup(BridgeSlashGroup):
    def __init__(self, callback, *args, translatable_description: Translatable | None = None, **kwargs):
        self.translatable_description = translatable_description

        super().__init__(callback, *args, **kwargs)

    @property
    def description_localizations(self) -> dict[str, str]:
        if not self.translatable_description:
            return {}

        return {lang: self.translatable_description.translate(lang) for lang in translations.DISCORD_LANGS}

    @description_localizations.setter
    def description_localizations(self, value: dict[str, str]):
        pass
