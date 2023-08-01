from discord import Interaction

from api.translation import translations


class Translator:
    def __init__(self, lang: str = translations.FALLBACK_LANGUAGE):
        self.lang = lang

    @classmethod
    async def from_interaction(cls, interaction: Interaction):
        inst = cls()

        await inst.set_from_interaction(interaction)

        return inst

    @classmethod
    async def from_guild(cls, guild_id: int):
        inst = cls()

        await inst.set_from_guild(guild_id)

        return inst

    async def set_from_interaction(self, interaction: Interaction):
        self.lang = interaction.locale.split("-")[0]

    async def set_from_guild(self, guild_id: int):
        self.lang = translations.FALLBACK_LANGUAGE

    def set_lang(self, lang: str):
        self.lang = lang

    def translate(self, key: str):
        return translations.translate(key, self.lang)

    def format(self, key: str, *args):
        return translations.fmt(key, self.lang, *args)
