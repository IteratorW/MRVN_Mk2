import discord

from api.translation import translations


class Translator:
    def __init__(self, lang: str = translations.FALLBACK_LANGUAGE):
        self.lang = lang

    async def for_guild(self, guild: discord.Guild):
        # TODO finish this when Guild Options are introduced
        self.lang = "beu"

    def translate(self, key: str):
        return translations.translate(key, self.lang)

    def format(self, key: str, *args):
        return translations.fmt(key, self.lang, *args)
