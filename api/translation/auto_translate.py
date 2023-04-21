import json
import logging
import os.path

from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException

from api.translation import translations
from api.translation.translations import DISCORD_LANGS

AUTO_TRANSLATIONS_PATH = "./auto_translations"
FALLBACK_PATH = f"{AUTO_TRANSLATIONS_PATH}/fallback.json"
LANG_PATH = f"{AUTO_TRANSLATIONS_PATH}/lang"

logger = logging.getLogger("Auto Translation")


def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


def start_auto_translation():
    fallback_translations = translations.translations[translations.FALLBACK_LANGUAGE]
    to_translate = {}

    if os.path.isfile(FALLBACK_PATH):
        with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
            previous = json.load(f)

        for k, v in fallback_translations.items():
            if k not in previous or previous[k] != v:
                to_translate[k] = v
    else:
        to_translate = fallback_translations

    if not len(to_translate):
        logger.info("Nothing new to translate")

        return

    logger.info(f"Auto-translating {len(to_translate)} lines from fallback lang {translations.FALLBACK_LANGUAGE}")

    if not os.path.isdir(AUTO_TRANSLATIONS_PATH):
        os.mkdir(AUTO_TRANSLATIONS_PATH)

    if not os.path.isdir(LANG_PATH):
        os.mkdir(LANG_PATH)

    values = [x.replace('\n', ' ').replace('\r', '') for x in to_translate.values()]

    for lang in DISCORD_LANGS:
        if lang in translations.translations:
            logger.info(f"Language {lang} is translated originally, skipping.")

            continue

        try:
            tr = GoogleTranslator(source="en", target=lang)
        except LanguageNotSupportedException:
            logger.error(f"Language {lang} is not supported, skipping.")

            continue

        keys = list(to_translate.keys())
        chunks_to_translate = list(chunks(list(values), 10))

        lang_path = f"{LANG_PATH}/{lang.split('-')[0]}.json"

        if os.path.isfile(lang_path):
            with open(lang_path, "r", encoding="utf-8") as f:
                translated = json.load(f)
        else:
            translated = {}

        for chunk_count, chunk in enumerate(chunks_to_translate):
            logger.info(f"Translating chunk {chunk_count + 1} of {len(chunks_to_translate)} for lang {lang}")

            result = tr.translate_batch(chunk)

            for i, string in enumerate(result):
                translated[keys[(chunk_count * 10) + i]] = string

        with open(lang_path, "w", encoding="utf-8") as f:
            json.dump(translated, f, indent=4, sort_keys=True, ensure_ascii=False)

    with open(FALLBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(fallback_translations, f, indent=4, sort_keys=True, ensure_ascii=False)

    logger.info("Done")
