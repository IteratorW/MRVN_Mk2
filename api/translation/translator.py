from discord import Interaction

from api.models import SettingGuildLanguage, SettingForceGuildLang
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
        if interaction.guild_id:
            setting = (await SettingForceGuildLang.get_or_none(guild_id=interaction.guild_id))

            if setting and setting.value:
                await self.set_from_guild(interaction.guild_id)

                return

        self.lang = interaction.locale.split("-")[0]

    async def set_from_guild(self, guild_id: int):
        self.lang = (await SettingGuildLanguage.get_or_create(guild_id=guild_id))[0].value

    def set_lang(self, lang: str):
        self.lang = lang

    def translate(self, key: str):
        return translations.translate(key, self.lang)

    def format(self, key: str, *args):
        return translations.fmt(key, self.lang, *args)
