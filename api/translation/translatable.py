from api.translation import translations


class Translatable(str):
    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return self.key

    def translate(self, lang: str = translations.FALLBACK_LANGUAGE) -> str:
        return translations.translate(self.key, lang)
