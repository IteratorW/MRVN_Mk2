import logging
import os
import pkgutil
from collections import defaultdict
from types import ModuleType

FALLBACK_LANGUAGE = "en"

translations = defaultdict(list[ModuleType])

logger = logging.getLogger("Translations")


def load_from_package(module: ModuleType):
    for importer, name, _ in pkgutil.iter_modules([os.path.dirname(module.__file__)]):
        m = importer.find_module(name).load_module(name)

        translations[name].append(m)


def find_in_module(key: str, module: ModuleType):
    try:
        return getattr(module, key)
    except AttributeError:
        return None


def translate(key: str, lang: str):
    for module in translations[lang]:
        if (translation := find_in_module(key, module)) is not None:
            return translation

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
