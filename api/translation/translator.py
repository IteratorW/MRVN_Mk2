from discord import Interaction, Guild

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
    def from_guild(cls, guild: Guild):
        inst = cls()

        inst.set_from_guild(guild)

        return inst

    def set_from_interaction(self, interaction: Interaction):
        self.lang = interaction.locale.split("-")[0]

    async def set_from_guild(self, guild: Guild):
        # TODO finish this when Guild Options are introduced
        self.lang = "beu"

    def translate(self, key: str):
        return translations.translate(key, self.lang)

    def format(self, key: str, *args):
        return translations.fmt(key, self.lang, *args)
