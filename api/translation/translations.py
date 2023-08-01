import json
import logging
import os
from collections import defaultdict

FALLBACK_LANGUAGE = "en"
DISCORD_LANGS = ["bg", "zh-CN", "cs", "fr", "de", "it", "ja", "ko", "pl", "ru", "uk"]

translations = defaultdict(dict[str, str])

logger = logging.getLogger("Translations")


def load_from_path(path: str):
    for file in [f for f in os.listdir(path) if os.path.isfile(f"{path}/{f}")]:
        lang = file.split(".")[0]

        with open(f"{path}/{file}", "r", encoding="utf-8") as f:
            lang_dict = json.load(f)

        translations[lang].update(lang_dict)


def translate(key: str, lang: str):
    if lang not in translations:
        if lang == FALLBACK_LANGUAGE:
            logger.error("Fallback language doesn't exist.")

            return key

        return translate(key, FALLBACK_LANGUAGE)

    try:
        text = translations[lang][key]

        return text
    except KeyError:
        # If not found for this lang, try to fall back to default

        if lang != FALLBACK_LANGUAGE:
            return translate(key, FALLBACK_LANGUAGE)

        logger.error(f"Translation not found in fallback language for key {key}")

    return key


def fmt(key: str, lang: str, *args):
    value = translate(key, lang)

    try:
        return value % args
    except (ValueError, TypeError):
        return value
