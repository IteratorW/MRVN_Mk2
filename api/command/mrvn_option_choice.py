from discord import OptionChoice

from api.translation import translations
from api.translation.translatable import Translatable


class MrvnOptionChoice(OptionChoice):
    def __init__(self, name: str | Translatable, value: str | int | float | None = None):
        self.translatable_name: Translatable | None = None

        if isinstance(name, Translatable):
            self.translatable_name = name
            name = self.translatable_name.translate()  # Translate to fallback lang

        super().__init__(name, value, None)

    @property
    def name_localizations(self) -> dict[str, str]:
        if not self.translatable_name:
            return {}

        return {lang: self.translatable_name.translate(lang) for lang in translations.DISCORD_LANGS}

    @name_localizations.setter
    def name_localizations(self, value: dict[str, str]):
        pass
