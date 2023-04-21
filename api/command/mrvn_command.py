import logging

from discord.ext.bridge import BridgeCommand, BridgeExtCommand, BridgeSlashCommand

from api.translation import translations
from api.translation.translatable import Translatable

logger = logging.getLogger("MRVN Commands")


class MrvnCommand(BridgeCommand):
    def __init__(self, callback, **kwargs):
        super().__init__(callback, **kwargs)

        self.translatable_description: Translatable | None = None

        if isinstance((desc := kwargs.get("description", None)), Translatable):
            self.translatable_description = desc
        elif desc is None:
            self.translatable_description = Translatable("mrvn_api_command_no_desc")

        # Translate to fallback language
        if self.translatable_description is not None:
            kwargs["description"] = self.translatable_description.translate()

        self.slash_variant: MrvnSlashCommand = kwargs.pop(
            "slash_variant", None
        ) or MrvnSlashCommand(callback, self.translatable_description, **kwargs)
        self.ext_variant: MrvnPrefixCommand = kwargs.pop(
            "ext_variant", None
        ) or MrvnPrefixCommand(callback, **kwargs)


class MrvnPrefixCommand(BridgeExtCommand):
    pass


class MrvnSlashCommand(BridgeSlashCommand):
    def __init__(self, func, translatable_description: Translatable | None = None, **kwargs):
        self.translatable_description = translatable_description

        super().__init__(func, **kwargs)

    @property
    def description_localizations(self) -> dict[str, str]:
        if not self.translatable_description:
            return {}

        return {lang: self.translatable_description.translate(lang) for lang in translations.DISCORD_LANGS}

    @description_localizations.setter
    def description_localizations(self, value: dict[str, str]):
        pass
