import json
import logging
import os.path

from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException

from api.translation import translations

DISCORD_LANGS = ["bg", "zh-CN", "cs", "fr", "de", "it", "ja", "ko", "pl", "ru", "uk"]

logger = logging.getLogger("Auto Translation")

translator_index = -1


def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


def start_auto_translation():
    to_translate = translations.translations[translations.FALLBACK_LANGUAGE]

    logger.info(f"Auto-translating {len(to_translate)} lines from fallback lang {translations.FALLBACK_LANGUAGE}")

    if not os.path.isdir("auto_translations"):
        os.mkdir("auto_translations")

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

        translated = {}

        for chunk_count, chunk in enumerate(chunks_to_translate):
            logger.info(f"Translating chunk {chunk_count + 1} of {len(chunks_to_translate)} for lang {lang}")

            result = tr.translate_batch(chunk)

            for i, string in enumerate(result):
                translated[keys[(chunk_count * 10) + i]] = string

        with open(f"auto_translations/{lang.split('-')[0]}.json", "w", encoding="utf-8") as f:
            json.dump(translated, f, indent=4, sort_keys=True, ensure_ascii=False)

    logger.info("Done")
