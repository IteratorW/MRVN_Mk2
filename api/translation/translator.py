from discord import Interaction

from api.models import SettingGuildLanguage
from api.translation import translations


class Translator:
    def __init__(self, lang: str = translations.FALLBACK_LANGUAGE):
        self.lang = lang

    @classmethod
    def from_interaction(cls, interaction: Interaction):
        inst = cls()

        inst.set_from_interaction(interaction)

        return inst

    @classmethod
    async def from_guild(cls, guild_id: int):
        inst = cls()

        await inst.set_from_guild(guild_id)

        return inst

    def set_from_interaction(self, interaction: Interaction):
        self.lang = interaction.locale.split("-")[0]

    async def set_from_guild(self, guild_id: int):
        self.lang = (await SettingGuildLanguage.get_or_create(guild_id=guild_id))[0].value

    def set_lang(self, lang: str):
        self.lang = lang

    def translate(self, key: str):
        return translations.translate(key, self.lang)

    def format(self, key: str, *args):
        return translations.fmt(key, self.lang, *args)
