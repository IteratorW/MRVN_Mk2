from discord import Option

from api.translation import translations
from api.translation.translatable import Translatable


class MrvnOption(Option):
    def __init__(self, *args, **kwargs):
        self.translatable_description: Translatable | None = None

        if isinstance(desc := kwargs.get("description", None), Translatable):
            self.translatable_description = desc
        elif desc is None:
            self.translatable_description = Translatable("mrvn_api_command_no_desc")

        # Translate to fallback language
        if self.translatable_description is not None:
            kwargs["description"] = self.translatable_description.translate()

        super().__init__(*args, **kwargs)

    @property
    def description_localizations(self) -> dict[str, str]:
        if self.translatable_description is None:
            return {}

        return {lang: self.translatable_description.translate(lang) for lang in translations.DISCORD_LANGS}

    @description_localizations.setter
    def description_localizations(self, value: dict[str, str]):
        pass


def mrvn_option(name, type=None, **kwargs):
    def decorator(func):
        nonlocal type
        type = type or func.__annotations__.get(name, str)
        if parameter := kwargs.get("parameter_name"):
            func.__annotations__[parameter] = MrvnOption(type, name=name, **kwargs)
        else:
            func.__annotations__[name] = MrvnOption(type, **kwargs)
        return func

    return decorator
